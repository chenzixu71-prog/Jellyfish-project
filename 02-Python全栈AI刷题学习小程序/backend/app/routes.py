from pathlib import Path

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from app import config
from app.schemas import (
    ApiResponse,
    GenerateQuizRequest,
    GenerateReportRequest,
    KnowledgeBaseCreateRequest,
    KnowledgeBaseQuizRequest,
    KnowledgeBaseSupplementRequest,
    RegenerateWeakQuizRequest,
    SubmitAnswerRequest,
    WechatLoginRequest,
)
from app.services.asset_parser import parse_learning_assets
from app.services.auth_service import AuthError, get_bearer_token, login_with_wechat
from app.services.knowledge_base_service import (
    create_knowledge_base,
    get_knowledge_base,
    list_knowledge_bases,
    start_quiz_from_knowledge_base,
    supplement_knowledge_base,
)
from app.services.quiz_service import (
    create_quiz,
    generate_report,
    get_challenge_history,
    get_daily_challenge,
    get_learning_profile,
    get_report_detail,
    get_report_history,
    get_wrong_questions,
    regenerate_weak_quiz,
    submit_answer,
)
from app.storage.memory_store import store


LEVELS = [
    {
        "id": "level-1",
        "title": "水母 DIY 第一关",
        "description": "把一个想学的知识变成可闯关练习题。",
        "status": "unlocked",
    },
    {
        "id": "level-2",
        "title": "即时反馈练习",
        "description": "理解答题后为什么要立刻给出正确答案和讲解。",
        "status": "locked",
    },
]

QUESTIONS = {
    "level-1": [
        {
            "id": "q-1",
            "type": "single-choice",
            "title": "水母diy学习助手第一版最应该先完成哪条闭环？",
            "options": [
                "全网排行榜、PK、VIP 付费",
                "文本输入、AI 出题、答题反馈、复盘报告",
                "视频解析、数字人、语音读题",
                "企业培训后台和复杂权限",
            ],
        }
    ]
}


router = APIRouter()


def ok(data=None, message="ok") -> ApiResponse:
    return ApiResponse(code=0, message=message, data=data)


def public_quiz_payload(quiz) -> dict:
    payload = quiz.model_dump()
    for question in payload.get("questions", []):
        question.pop("answer", None)
        question.pop("explanation", None)
    return payload


def apply_original_upload_name(
    files: list[UploadFile], images: list[UploadFile], original_name: str
) -> None:
    uploads = [*files, *images]
    if original_name and len(uploads) == 1:
        uploads[0].filename = Path(original_name).name


def resolve_learning_owner(session_id: str, authorization: str | None = None) -> str:
    if not authorization:
        return session_id
    try:
        token = get_bearer_token(authorization)
        user = store.get_user_by_token(token)
        if not user:
            raise AuthError("invalid token")
        return user.id
    except AuthError as exc:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录") from exc


@router.get("/health", response_model=ApiResponse)
def health():
    return ok(
        {
            "service": "ai-quiz-miniapp-backend",
            "product": "水母diy学习助手",
            "status": "running",
            "aiModel": config.AI_MODEL,
            "environment": config.ENVIRONMENT,
            "storageBackend": config.STORAGE_BACKEND,
        }
    )


@router.get("/ready", response_model=ApiResponse)
def ready():
    errors = config.production_configuration_errors()
    if errors:
        raise HTTPException(status_code=503, detail={"checks": errors})
    return ok(
        {
            "status": "ready",
            "aiProvider": config.AI_PROVIDER,
            "searchProvider": config.SEARCH_PROVIDER,
            "wechatAuthMode": config.WECHAT_AUTH_MODE,
            "storageBackend": config.STORAGE_BACKEND,
        }
    )


@router.get("/api/levels", response_model=ApiResponse)
def list_levels():
    return ok(LEVELS)


@router.get("/api/questions", response_model=ApiResponse)
def list_questions(levelId: str = "level-1"):
    return ok(QUESTIONS.get(levelId, []))


@router.post("/api/auth/wechat-login", response_model=ApiResponse)
def wechat_login(payload: WechatLoginRequest):
    try:
        result = login_with_wechat(payload.code, payload.sessionId)
        return ok(result.model_dump())
    except AuthError:
        return ApiResponse(code=1001, message="登录失败，请稍后重试", data=None)


@router.get("/api/me", response_model=ApiResponse)
def current_user(authorization: str | None = Header(default=None)):
    try:
        token = get_bearer_token(authorization)
        user = store.get_user_by_token(token)
        if not user:
            raise AuthError("invalid token")
        return ok(store.get_current_user_profile(user).model_dump())
    except AuthError:
        return ApiResponse(code=1002, message="登录已失效，请重新登录", data=None)


@router.post("/api/generate-quiz", response_model=ApiResponse)
def generate_quiz(payload: GenerateQuizRequest, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(payload.sessionId, authorization)
    quiz = create_quiz(owner_id, payload.content, payload.webSearchEnabled)
    return ok(public_quiz_payload(quiz))


@router.post("/api/generate-quiz-from-assets", response_model=ApiResponse)
async def generate_quiz_from_assets(
    sessionId: str = Form(...),
    content: str = Form(""),
    webSearchEnabled: bool = Form(False),
    files: list[UploadFile] = File(default=[]),
    images: list[UploadFile] = File(default=[]),
    authorization: str | None = Header(default=None),
):
    parsed = await parse_learning_assets(content, files, images)
    owner_id = resolve_learning_owner(sessionId, authorization)
    quiz = create_quiz(owner_id, parsed.content, webSearchEnabled)
    payload = public_quiz_payload(quiz)
    payload["source"] = {
        "fileCount": parsed.file_count,
        "imageCount": parsed.image_count,
        "notes": parsed.notes,
    }
    return ok(payload)


@router.post("/api/knowledge-bases", response_model=ApiResponse)
def create_kb(payload: KnowledgeBaseCreateRequest, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(payload.sessionId, authorization)
    knowledge_base = create_knowledge_base(
        owner_id,
        payload.content,
        payload.title,
        payload.webSearchEnabled,
    )
    return ok(knowledge_base.model_dump())


@router.post("/api/knowledge-bases/from-assets", response_model=ApiResponse)
async def create_kb_from_assets(
    sessionId: str = Form(...),
    title: str = Form(""),
    content: str = Form(""),
    webSearchEnabled: bool = Form(False),
    files: list[UploadFile] = File(default=[]),
    images: list[UploadFile] = File(default=[]),
    originalName: str = Form(""),
    authorization: str | None = Header(default=None),
):
    apply_original_upload_name(files, images, originalName)
    parsed = await parse_learning_assets(content, files, images)
    owner_id = resolve_learning_owner(sessionId, authorization)
    knowledge_base = create_knowledge_base(
        owner_id,
        parsed.content,
        title,
        webSearchEnabled,
    )
    payload = knowledge_base.model_dump()
    payload["upload"] = {
        "fileCount": parsed.file_count,
        "imageCount": parsed.image_count,
        "notes": parsed.notes,
    }
    return ok(payload)


@router.get("/api/knowledge-bases", response_model=ApiResponse)
def knowledge_bases(sessionId: str, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(sessionId, authorization)
    return ok([item.model_dump() for item in list_knowledge_bases(owner_id)])


@router.get("/api/knowledge-bases/{knowledge_base_id}", response_model=ApiResponse)
def knowledge_base_detail(
    knowledge_base_id: str,
    sessionId: str,
    authorization: str | None = Header(default=None),
):
    owner_id = resolve_learning_owner(sessionId, authorization)
    return ok(get_knowledge_base(owner_id, knowledge_base_id).model_dump())


@router.post("/api/knowledge-bases/{knowledge_base_id}/supplements", response_model=ApiResponse)
def supplement_kb(
    knowledge_base_id: str,
    payload: KnowledgeBaseSupplementRequest,
    authorization: str | None = Header(default=None),
):
    owner_id = resolve_learning_owner(payload.sessionId, authorization)
    knowledge_base = supplement_knowledge_base(
        owner_id,
        knowledge_base_id,
        payload.content,
        payload.webSearchEnabled,
    )
    return ok(knowledge_base.model_dump())


@router.post("/api/knowledge-bases/{knowledge_base_id}/supplements/from-assets", response_model=ApiResponse)
async def supplement_kb_from_assets(
    knowledge_base_id: str,
    sessionId: str = Form(...),
    content: str = Form(""),
    webSearchEnabled: bool = Form(False),
    files: list[UploadFile] = File(default=[]),
    images: list[UploadFile] = File(default=[]),
    originalName: str = Form(""),
    authorization: str | None = Header(default=None),
):
    apply_original_upload_name(files, images, originalName)
    parsed = await parse_learning_assets(content, files, images)
    owner_id = resolve_learning_owner(sessionId, authorization)
    knowledge_base = supplement_knowledge_base(
        owner_id,
        knowledge_base_id,
        parsed.content,
        webSearchEnabled,
    )
    payload = knowledge_base.model_dump()
    payload["upload"] = {
        "fileCount": parsed.file_count,
        "imageCount": parsed.image_count,
        "notes": parsed.notes,
    }
    return ok(payload)


@router.post("/api/knowledge-bases/{knowledge_base_id}/quiz", response_model=ApiResponse)
def knowledge_base_quiz(
    knowledge_base_id: str,
    payload: KnowledgeBaseQuizRequest,
    authorization: str | None = Header(default=None),
):
    owner_id = resolve_learning_owner(payload.sessionId, authorization)
    quiz = start_quiz_from_knowledge_base(owner_id, knowledge_base_id)
    return ok(public_quiz_payload(quiz))


@router.post("/api/submit-answer", response_model=ApiResponse)
def answer_question(payload: SubmitAnswerRequest, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(payload.sessionId, authorization)
    result = submit_answer(
        owner_id,
        payload.quizId,
        payload.questionId,
        payload.answer,
    )
    return ok(result.model_dump())


@router.post("/api/generate-report", response_model=ApiResponse)
def report(payload: GenerateReportRequest, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(payload.sessionId, authorization)
    generated_report = generate_report(owner_id, payload.quizId)
    return ok(generated_report.model_dump())


@router.get("/api/wrong-questions", response_model=ApiResponse)
def wrong_questions(sessionId: str, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(sessionId, authorization)
    return ok([item.model_dump() for item in get_wrong_questions(owner_id)])


@router.post("/api/regenerate-weak-quiz", response_model=ApiResponse)
def weak_quiz(payload: RegenerateWeakQuizRequest, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(payload.sessionId, authorization)
    quiz = regenerate_weak_quiz(owner_id, payload.quizId)
    return ok(public_quiz_payload(quiz))


@router.get("/api/report-history", response_model=ApiResponse)
def report_history(sessionId: str, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(sessionId, authorization)
    return ok([item.model_dump() for item in get_report_history(owner_id)])


@router.get("/api/report-detail", response_model=ApiResponse)
def report_detail(
    sessionId: str,
    quizId: str,
    authorization: str | None = Header(default=None),
):
    owner_id = resolve_learning_owner(sessionId, authorization)
    saved_report = get_report_detail(owner_id, quizId)
    if not saved_report:
        return ApiResponse(code=1003, message="报告不存在，请先完成闯关并生成报告", data=None)
    return ok(saved_report.model_dump())


@router.get("/api/challenge-history", response_model=ApiResponse)
def challenge_history(sessionId: str, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(sessionId, authorization)
    return ok([item.model_dump() for item in get_challenge_history(owner_id)])


@router.get("/api/daily-challenge", response_model=ApiResponse)
def daily_challenge(sessionId: str, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(sessionId, authorization)
    return ok(get_daily_challenge(owner_id).model_dump())


@router.get("/api/profile", response_model=ApiResponse)
def profile(sessionId: str, authorization: str | None = Header(default=None)):
    owner_id = resolve_learning_owner(sessionId, authorization)
    return ok(get_learning_profile(owner_id).model_dump())
