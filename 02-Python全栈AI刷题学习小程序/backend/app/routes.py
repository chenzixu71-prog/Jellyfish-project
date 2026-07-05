import json

from app.config import AI_MODEL, DATABASE_URL


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


def json_response(status, data=None, message="ok"):
    return status, json.dumps(
        {
            "code": 0 if status < 400 else status,
            "message": message,
            "data": data,
        },
        ensure_ascii=False,
    )


def route_request(method, path, query):
    if method != "GET":
        return json_response(405, None, "method not allowed")

    if path == "/health":
        return json_response(
            200,
            {
                "service": "ai-quiz-miniapp-backend",
                "product": "水母diy学习助手",
                "status": "running",
                "databaseUrl": DATABASE_URL,
                "aiModel": AI_MODEL,
            },
        )

    if path == "/api/levels":
        return json_response(200, LEVELS)

    if path == "/api/questions":
        level_id = query.get("levelId", ["level-1"])[0]
        return json_response(200, QUESTIONS.get(level_id, []))

    return json_response(404, None, "route not found")
