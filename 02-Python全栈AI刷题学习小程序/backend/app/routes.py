from fastapi import APIRouter, File, Form, UploadFile

from app.config import AI_MODEL
from app.schemas import (
    ApiResponse,
    GenerateQuizRequest,
    GenerateReportRequest,
    RegenerateWeakQuizRequest,
    SubmitAnswerRequest,
    WechatLoginRequest,
)
from app.services.asset_parser import parse_learning_assets
from app.services.auth_service import AuthError, login_with_wechat
from app.services.quiz_service import (
    create_quiz,
    generate_report,
    get_daily_challenge,
    get_learning_profile,
    get_report_history,
    get_wrong_questions,
    regenerate_weak_quiz,
    submit_answer,
)


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


@router.get("/health", response_model=ApiResponse)
def health():
    return ok(
        {
            "service": "ai-quiz-miniapp-backend",
            "product": "水母diy学习助手",
            "status": "running",
            "aiModel": AI_MODEL,
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


@router.post("/api/generate-quiz", response_model=ApiResponse)
def generate_quiz(payload: GenerateQuizRequest):
    quiz = create_quiz(payload.sessionId, payload.content)
    return ok(quiz.model_dump())


@router.post("/api/generate-quiz-from-assets", response_model=ApiResponse)
async def generate_quiz_from_assets(
    sessionId: str = Form(...),
    content: str = Form(""),
    files: list[UploadFile] = File(default=[]),
    images: list[UploadFile] = File(default=[]),
):
    parsed = await parse_learning_assets(content, files, images)
    quiz = create_quiz(sessionId, parsed.content)
    payload = quiz.model_dump()
    payload["source"] = {
        "fileCount": parsed.file_count,
        "imageCount": parsed.image_count,
        "notes": parsed.notes,
    }
    return ok(payload)


@router.post("/api/submit-answer", response_model=ApiResponse)
def answer_question(payload: SubmitAnswerRequest):
    result = submit_answer(
        payload.sessionId,
        payload.quizId,
        payload.questionId,
        payload.answer,
    )
    return ok(result.model_dump())


@router.post("/api/generate-report", response_model=ApiResponse)
def report(payload: GenerateReportRequest):
    generated_report = generate_report(payload.sessionId, payload.quizId)
    return ok(generated_report.model_dump())


@router.get("/api/wrong-questions", response_model=ApiResponse)
def wrong_questions(sessionId: str):
    return ok([item.model_dump() for item in get_wrong_questions(sessionId)])


@router.post("/api/regenerate-weak-quiz", response_model=ApiResponse)
def weak_quiz(payload: RegenerateWeakQuizRequest):
    quiz = regenerate_weak_quiz(payload.sessionId, payload.quizId)
    return ok(quiz.model_dump())


@router.get("/api/report-history", response_model=ApiResponse)
def report_history(sessionId: str):
    return ok([item.model_dump() for item in get_report_history(sessionId)])


@router.get("/api/daily-challenge", response_model=ApiResponse)
def daily_challenge(sessionId: str):
    return ok(get_daily_challenge(sessionId).model_dump())


@router.get("/api/profile", response_model=ApiResponse)
def profile(sessionId: str):
    return ok(get_learning_profile(sessionId).model_dump())
