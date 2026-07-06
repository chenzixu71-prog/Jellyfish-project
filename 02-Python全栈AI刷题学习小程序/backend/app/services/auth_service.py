import hashlib
import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import urlopen

from app.config import WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_AUTH_MODE
from app.schemas import WechatLoginResponse
from app.storage.memory_store import store


class AuthError(Exception):
    pass


@dataclass(frozen=True)
class WechatSession:
    openid: str
    session_key: str
    unionid: str | None = None


def exchange_wechat_code(code: str) -> WechatSession:
    if WECHAT_AUTH_MODE != "wechat":
        if code == "fail-code":
            raise AuthError("mock code exchange failed")
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()[:18]
        return WechatSession(
            openid=f"mock-openid-{digest}",
            session_key=f"mock-session-{digest}",
        )

    if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        raise AuthError("wechat app credentials are not configured")

    params = urlencode(
        {
            "appid": WECHAT_APP_ID,
            "secret": WECHAT_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    with urlopen(f"https://api.weixin.qq.com/sns/jscode2session?{params}", timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("errcode"):
        raise AuthError(str(payload.get("errmsg") or "wechat code2Session failed"))

    openid = payload.get("openid")
    session_key = payload.get("session_key")
    if not openid or not session_key:
        raise AuthError("wechat code2Session response is incomplete")

    return WechatSession(
        openid=openid,
        session_key=session_key,
        unionid=payload.get("unionid"),
    )


def login_with_wechat(code: str, session_id: str) -> WechatLoginResponse:
    wechat_session = exchange_wechat_code(code)
    user = store.get_or_create_wechat_user(wechat_session.openid)
    token = store.create_auth_token(user.id)
    merged = store.merge_guest_session_into_user(session_id, user.id)
    return WechatLoginResponse(token=token, user=user, merged=merged)


def get_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthError("missing authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError("invalid authorization header")
    return token
