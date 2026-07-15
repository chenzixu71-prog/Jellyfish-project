from fastapi.testclient import TestClient

from app import config
from app.main import app
from app.storage.memory_store import store


config.AI_PROVIDER = "mock"
config.SEARCH_PROVIDER = "mock"

client = TestClient(app)


def stored_answer(quiz_id: str, question_id: str) -> list[str]:
    quiz = store.get_quiz(quiz_id)
    assert quiz is not None
    question = next(item for item in quiz.questions if item.id == question_id)
    return question.answer


def test_health_returns_service_status():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["status"] == "running"
    assert body["data"]["product"] == "水母diy学习助手"


def test_ready_returns_provider_and_storage_status():
    response = client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["status"] == "ready"
    assert body["data"]["aiProvider"] == config.AI_PROVIDER
    assert body["data"]["storageBackend"] == config.STORAGE_BACKEND


def test_wechat_login_creates_user_and_token():
    response = client.post(
        "/api/auth/wechat-login",
        json={"code": "test-login-code", "sessionId": "guest-session"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["token"]
    assert body["data"]["user"]["id"]
    assert body["data"]["user"]["displayName"] == "水母学员"
    assert body["data"]["user"]["avatarUrl"] == ""
    assert body["data"]["user"]["loginType"] == "wechat"


def test_wechat_login_reuses_existing_user():
    first = client.post(
        "/api/auth/wechat-login",
        json={"code": "same-login-code", "sessionId": "guest-session-a"},
    ).json()["data"]
    second = client.post(
        "/api/auth/wechat-login",
        json={"code": "same-login-code", "sessionId": "guest-session-b"},
    ).json()["data"]

    assert first["user"]["id"] == second["user"]["id"]
    assert first["token"] != second["token"]


def test_wechat_login_returns_business_error_when_code_exchange_fails():
    response = client.post(
        "/api/auth/wechat-login",
        json={"code": "fail-code", "sessionId": "guest-session"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1001
    assert "登录失败" in body["message"]
    assert body["data"] is None


def test_me_returns_current_user_profile_with_valid_token():
    login = client.post(
        "/api/auth/wechat-login",
        json={"code": "profile-code", "sessionId": "profile-session"},
    ).json()["data"]

    response = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {login['token']}"},
    )

    assert response.status_code == 200
    body = response.json()
    profile = body["data"]
    assert body["code"] == 0
    assert profile["id"] == login["user"]["id"]
    assert profile["displayName"] == "水母学员"
    assert profile["avatarUrl"] == ""
    assert profile["loginType"] == "wechat"
    assert profile["level"] == 1
    assert profile["exp"] == 0
    assert profile["nextLevelExp"] == 100
    assert profile["streakDays"] == 1
    assert profile["totalAnswered"] == 0
    assert profile["totalCorrect"] == 0
    assert profile["totalSessions"] == 0
    assert profile["accuracy"] == 0
    assert len(profile["badges"]) >= 3


def test_me_returns_business_error_without_token():
    response = client.get("/api/me")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1002
    assert "登录已失效" in body["message"]
    assert body["data"] is None


def test_me_returns_business_error_with_invalid_token():
    response = client.get(
        "/api/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1002
    assert "登录已失效" in body["message"]
    assert body["data"] is None


def test_wechat_login_binds_guest_learning_data_once():
    session_id = "bind-guest-session"
    generated = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": session_id,
            "inputType": "text",
            "content": "learn ports and databases",
            "questionCount": 5,
        },
    ).json()["data"]

    for question in generated["questions"]:
        client.post(
            "/api/submit-answer",
            json={
                "sessionId": session_id,
                "quizId": generated["quizId"],
                "questionId": question["id"],
                "answer": stored_answer(generated["quizId"], question["id"]),
            },
        )

    client.post(
        "/api/generate-report",
        json={"sessionId": session_id, "quizId": generated["quizId"]},
    )

    first_login = client.post(
        "/api/auth/wechat-login",
        json={"code": "bind-guest-code", "sessionId": session_id},
    ).json()["data"]
    assert first_login["merged"]["answers"] == 5
    assert first_login["merged"]["reports"] == 1
    assert first_login["merged"]["profileStats"] is True

    profile = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {first_login['token']}"},
    ).json()["data"]
    assert profile["totalAnswered"] == 5
    assert profile["totalCorrect"] == 5
    assert profile["totalSessions"] == 1

    second_login = client.post(
        "/api/auth/wechat-login",
        json={"code": "bind-guest-code", "sessionId": session_id},
    ).json()["data"]
    assert second_login["merged"]["answers"] == 0
    assert second_login["merged"]["reports"] == 0
    assert second_login["merged"]["profileStats"] is False

    profile_after_repeat_login = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {second_login['token']}"},
    ).json()["data"]
    assert profile_after_repeat_login["totalAnswered"] == 5
    assert profile_after_repeat_login["totalCorrect"] == 5
    assert profile_after_repeat_login["totalSessions"] == 1


def test_learning_endpoints_use_authenticated_user_identity():
    login = client.post(
        "/api/auth/wechat-login",
        json={"code": "owner-learning-code", "sessionId": "owner-guest-session"},
    ).json()["data"]
    headers = {"Authorization": f"Bearer {login['token']}"}

    generated = client.post(
        "/api/generate-quiz",
        headers=headers,
        json={
            "sessionId": "owner-local-session",
            "inputType": "text",
            "content": "learn HTTP requests",
            "questionCount": 5,
        },
    ).json()["data"]

    first_question = generated["questions"][0]
    client.post(
        "/api/submit-answer",
        headers=headers,
        json={
            "sessionId": "owner-local-session",
            "quizId": generated["quizId"],
            "questionId": first_question["id"],
            "answer": stored_answer(generated["quizId"], first_question["id"]),
        },
    )

    profile = client.get("/api/me", headers=headers).json()["data"]
    assert profile["totalAnswered"] == 1
    assert profile["totalCorrect"] == 1


def test_learning_endpoint_rejects_invalid_token_instead_of_using_guest_session():
    response = client.post(
        "/api/generate-quiz",
        headers={"Authorization": "Bearer invalid-token"},
        json={
            "sessionId": "must-not-become-guest",
            "inputType": "text",
            "content": "learn authentication boundaries",
            "questionCount": 5,
        },
    )

    assert response.status_code == 401
    assert "登录已失效" in response.json()["detail"]


def test_challenge_history_returns_authenticated_reports():
    login = client.post(
        "/api/auth/wechat-login",
        json={"code": "history-code", "sessionId": "history-guest-session"},
    ).json()["data"]
    headers = {"Authorization": f"Bearer {login['token']}"}
    session_id = "history-local-session"

    generated = client.post(
        "/api/generate-quiz",
        headers=headers,
        json={
            "sessionId": session_id,
            "inputType": "text",
            "content": "learn MySQL basics",
            "questionCount": 5,
        },
    ).json()["data"]

    for question in generated["questions"]:
        client.post(
            "/api/submit-answer",
            headers=headers,
            json={
                "sessionId": session_id,
                "quizId": generated["quizId"],
                "questionId": question["id"],
                "answer": stored_answer(generated["quizId"], question["id"]),
            },
        )

    client.post(
        "/api/generate-report",
        headers=headers,
        json={"sessionId": session_id, "quizId": generated["quizId"]},
    )

    history = client.get(
        "/api/challenge-history",
        headers=headers,
        params={"sessionId": session_id},
    ).json()["data"]

    assert len(history) == 1
    assert history[0]["quizId"] == generated["quizId"]
    assert history[0]["title"]
    assert history[0]["score"] == 5
    assert history[0]["total"] == 5
    assert history[0]["mastery"] == 100
    assert history[0]["completedAt"]


def test_report_history_and_detail_return_saved_report():
    login = client.post(
        "/api/auth/wechat-login",
        json={"code": "report-history-code", "sessionId": "report-history-guest"},
    ).json()["data"]
    headers = {"Authorization": f"Bearer {login['token']}"}
    session_id = "report-history-session"

    generated = client.post(
        "/api/generate-quiz",
        headers=headers,
        json={
            "sessionId": session_id,
            "inputType": "text",
            "content": "learn report history",
            "questionCount": 5,
        },
    ).json()["data"]

    for question in generated["questions"]:
        client.post(
            "/api/submit-answer",
            headers=headers,
            json={
                "sessionId": session_id,
                "quizId": generated["quizId"],
                "questionId": question["id"],
                "answer": stored_answer(generated["quizId"], question["id"]),
            },
        )

    report = client.post(
        "/api/generate-report",
        headers=headers,
        json={"sessionId": session_id, "quizId": generated["quizId"]},
    ).json()["data"]
    assert report["completedAt"]

    history = client.get(
        "/api/report-history",
        headers=headers,
        params={"sessionId": session_id},
    ).json()["data"]
    assert history[0]["quizId"] == generated["quizId"]
    assert history[0]["completedAt"] == report["completedAt"]

    detail = client.get(
        "/api/report-detail",
        headers=headers,
        params={"sessionId": session_id, "quizId": generated["quizId"]},
    ).json()["data"]
    assert detail["quizId"] == generated["quizId"]
    assert detail["summary"] == report["summary"]
    assert detail["completedAt"] == report["completedAt"]


def test_wrong_book_uses_authenticated_identity_and_regenerates_quiz():
    login = client.post(
        "/api/auth/wechat-login",
        json={"code": "wrong-book-code", "sessionId": "wrong-book-guest"},
    ).json()["data"]
    headers = {"Authorization": f"Bearer {login['token']}"}
    session_id = "wrong-book-session"

    generated = client.post(
        "/api/generate-quiz",
        headers=headers,
        json={
            "sessionId": session_id,
            "inputType": "text",
            "content": "learn wrong book",
            "questionCount": 5,
        },
    ).json()["data"]
    first_question = generated["questions"][0]
    correct_answer = stored_answer(generated["quizId"], first_question["id"])
    wrong_answer = ["B"] if correct_answer != ["B"] else ["A"]

    client.post(
        "/api/submit-answer",
        headers=headers,
        json={
            "sessionId": session_id,
            "quizId": generated["quizId"],
            "questionId": first_question["id"],
            "answer": wrong_answer,
        },
    )

    wrong_questions = client.get(
        "/api/wrong-questions",
        headers=headers,
        params={"sessionId": session_id},
    ).json()["data"]
    assert len(wrong_questions) == 1
    assert wrong_questions[0]["stem"]
    assert wrong_questions[0]["selectedAnswer"] == wrong_answer
    assert wrong_questions[0]["correctAnswer"] == correct_answer
    assert wrong_questions[0]["explanation"]
    assert wrong_questions[0]["knowledge_point"]

    regenerated = client.post(
        "/api/regenerate-weak-quiz",
        headers=headers,
        json={"sessionId": session_id, "quizId": generated["quizId"]},
    ).json()["data"]
    assert regenerated["quizId"]
    assert len(regenerated["questions"]) == 5


def test_growth_profile_updates_exp_level_and_badges_after_learning():
    login = client.post(
        "/api/auth/wechat-login",
        json={"code": "growth-code", "sessionId": "growth-guest"},
    ).json()["data"]
    headers = {"Authorization": f"Bearer {login['token']}"}
    session_id = "growth-session"

    generated = client.post(
        "/api/generate-quiz",
        headers=headers,
        json={
            "sessionId": session_id,
            "inputType": "text",
            "content": "learn growth system",
            "questionCount": 5,
        },
    ).json()["data"]

    for question in generated["questions"]:
        client.post(
            "/api/submit-answer",
            headers=headers,
            json={
                "sessionId": session_id,
                "quizId": generated["quizId"],
                "questionId": question["id"],
                "answer": stored_answer(generated["quizId"], question["id"]),
            },
        )

    client.post(
        "/api/generate-report",
        headers=headers,
        json={"sessionId": session_id, "quizId": generated["quizId"]},
    )

    profile = client.get("/api/me", headers=headers).json()["data"]
    assert profile["exp"] == 60
    assert profile["level"] == 1
    assert profile["nextLevelExp"] == 100
    assert profile["streakDays"] == 1
    assert any(item["id"] == "first-quiz" and item["unlocked"] for item in profile["badges"])
    assert any(item["id"] == "perfect-run" and item["unlocked"] for item in profile["badges"])


def test_generate_quiz_returns_five_mixed_questions():
    response = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": "test-session",
            "inputType": "text",
            "content": "我想学习 Git 的 pull、commit、push",
            "questionCount": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    quiz = body["data"]
    assert body["code"] == 0
    assert quiz["quizId"]
    assert quiz["title"]
    assert len(quiz["questions"]) == 5

    types = [question["type"] for question in quiz["questions"]]
    assert types.count("single") == 3
    assert types.count("multiple") == 1
    assert types.count("judge") == 1

    for question in quiz["questions"]:
        assert question["id"]
        assert question["stem"]
        assert "answer" not in question
        assert "explanation" not in question
        assert question["knowledge_point"]
        assert question["difficulty"] in {"easy", "medium", "hard"}


def test_generate_quiz_returns_source_meta_when_web_search_enabled():
    response = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": "source-meta-session",
            "inputType": "text",
            "content": "我想学习最新的 Harness Engineering",
            "questionCount": 5,
            "webSearchEnabled": True,
        },
    )

    assert response.status_code == 200
    quiz = response.json()["data"]
    assert quiz["sourceMeta"]["enabled"] is True
    assert "sourceCount" in quiz["sourceMeta"]
    assert "toolCalls" in quiz["sourceMeta"]
    assert "warnings" in quiz["sourceMeta"]
    assert "sources" in quiz["sourceMeta"]


def test_create_list_supplement_and_quiz_from_knowledge_base():
    session_id = "kb-session"
    created = client.post(
        "/api/knowledge-bases",
        json={
            "sessionId": session_id,
            "title": "英语知识库",
            "content": "我想学习英语中的现在完成时。",
            "webSearchEnabled": False,
        },
    ).json()["data"]

    assert created["id"].startswith("kb-")
    assert created["title"] == "英语知识库"
    assert len(created["materials"]) == 1

    items = client.get(
        "/api/knowledge-bases",
        params={"sessionId": session_id},
    ).json()["data"]
    assert len(items) == 1
    assert items[0]["id"] == created["id"]
    assert items[0]["materialCount"] == 1

    detail = client.get(
        f"/api/knowledge-bases/{created['id']}",
        params={"sessionId": session_id},
    ).json()["data"]
    assert "现在完成时" in detail["content"]

    supplemented = client.post(
        f"/api/knowledge-bases/{created['id']}/supplements",
        json={
            "sessionId": session_id,
            "content": "补充：现在完成时常和 already、yet、ever 搭配。",
            "webSearchEnabled": False,
        },
    ).json()["data"]
    assert len(supplemented["materials"]) == 2
    assert "already" in supplemented["content"]

    quiz = client.post(
        f"/api/knowledge-bases/{created['id']}/quiz",
        json={"sessionId": session_id},
    ).json()["data"]
    assert quiz["quizId"]
    assert quiz["title"] == "英语知识库"
    assert len(quiz["questions"]) == 5
    assert all("answer" not in question for question in quiz["questions"])
    assert all("explanation" not in question for question in quiz["questions"])


def test_knowledge_base_limit_is_five_per_owner():
    session_id = "kb-limit-session"

    for index in range(5):
        response = client.post(
            "/api/knowledge-bases",
            json={
                "sessionId": session_id,
                "title": f"知识库 {index}",
                "content": f"学习主题 {index}",
                "webSearchEnabled": False,
            },
        )
        assert response.status_code == 200
        assert response.json()["code"] == 0

    rejected = client.post(
        "/api/knowledge-bases",
        json={
            "sessionId": session_id,
            "title": "第六个知识库",
            "content": "超过上限",
            "webSearchEnabled": False,
        },
    )

    assert rejected.status_code == 400
    assert "5" in rejected.json()["detail"]


def test_knowledge_base_from_assets_accepts_text_file():
    response = client.post(
        "/api/knowledge-bases/from-assets",
        data={
            "sessionId": "kb-asset-session",
            "title": "Redis 素材",
            "originalName": "redis.md",
        },
        files=[
            ("files", ("upload.bin", b"Redis keeps data in memory.", "application/octet-stream")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    kb = body["data"]
    assert body["code"] == 0
    assert kb["title"] == "Redis 素材"
    assert "Redis keeps data" in kb["content"]
    assert kb["upload"]["fileCount"] == 1


def test_wechat_login_binds_guest_knowledge_bases_once():
    session_id = "kb-bind-guest"
    created = client.post(
        "/api/knowledge-bases",
        json={
            "sessionId": session_id,
            "title": "游客知识库",
            "content": "游客先创建的知识库",
        },
    ).json()["data"]

    login = client.post(
        "/api/auth/wechat-login",
        json={"code": "kb-bind-code", "sessionId": session_id},
    ).json()["data"]

    assert login["merged"]["knowledgeBases"] == 1

    authed_items = client.get(
        "/api/knowledge-bases",
        headers={"Authorization": f"Bearer {login['token']}"},
        params={"sessionId": session_id},
    ).json()["data"]
    assert any(item["id"] == created["id"] for item in authed_items)


def test_generate_quiz_rejects_empty_content():
    response = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": "test-session",
            "inputType": "text",
            "content": "  ",
            "questionCount": 5,
        },
    )

    assert response.status_code == 422


def test_generate_quiz_from_assets_accepts_text_files_and_images(monkeypatch):
    monkeypatch.setattr(
        "app.services.asset_parser.try_ocr_image",
        lambda _raw: "Redis diagram: memory, key and value",
    )
    response = client.post(
        "/api/generate-quiz-from-assets",
        data={"sessionId": "asset-session", "content": "请结合上传素材出题"},
        files=[
            ("files", ("note.txt", b"Redis is an in-memory data store.", "text/plain")),
            ("images", ("diagram.png", b"fake-image-bytes", "image/png")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    quiz = body["data"]
    assert body["code"] == 0
    assert len(quiz["questions"]) == 5
    assert quiz["source"]["fileCount"] == 1
    assert quiz["source"]["imageCount"] == 1
    assert quiz["source"]["notes"]


def test_generate_quiz_from_assets_rejects_image_without_ocr_text(monkeypatch):
    monkeypatch.setattr("app.services.asset_parser.try_ocr_image", lambda _raw: "")
    response = client.post(
        "/api/generate-quiz-from-assets",
        data={"sessionId": "image-ocr-failed", "content": "图片学习资料"},
        files=[("images", ("blurred.png", b"fake-image", "image/png"))],
    )

    assert response.status_code == 422
    assert "未识别到可用文字" in response.json()["detail"]


def test_generate_quiz_from_assets_rejects_more_than_three_files():
    files = [
        ("files", (f"note-{index}.txt", b"hello", "text/plain"))
        for index in range(4)
    ]

    response = client.post(
        "/api/generate-quiz-from-assets",
        data={"sessionId": "too-many-files"},
        files=files,
    )

    assert response.status_code == 400
    assert "3" in response.json()["detail"]


def test_generate_quiz_from_assets_rejects_more_than_ten_images():
    files = [
        ("images", (f"image-{index}.png", b"image", "image/png"))
        for index in range(11)
    ]

    response = client.post(
        "/api/generate-quiz-from-assets",
        data={"sessionId": "too-many-images", "content": "图片学习资料"},
        files=files,
    )

    assert response.status_code == 400
    assert "10" in response.json()["detail"]


def test_generate_quiz_from_assets_rejects_unsupported_file_type():
    response = client.post(
        "/api/generate-quiz-from-assets",
        data={"sessionId": "bad-file"},
        files=[
            ("files", ("slides.pptx", b"binary", "application/vnd.ms-powerpoint")),
        ],
    )

    assert response.status_code == 400
    assert "txt/md/csv/json" in response.json()["detail"]


def test_submit_answer_scores_and_returns_explanation():
    generated = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": "answer-session",
            "inputType": "text",
            "content": "学习端口是什么",
            "questionCount": 5,
        },
    ).json()["data"]
    first_question = generated["questions"][0]
    correct_answer = stored_answer(generated["quizId"], first_question["id"])

    response = client.post(
        "/api/submit-answer",
        json={
            "sessionId": "answer-session",
            "quizId": generated["quizId"],
            "questionId": first_question["id"],
            "answer": correct_answer,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["isCorrect"] is True
    assert body["data"]["correctAnswer"] == correct_answer
    assert body["data"]["explanation"]


def test_submit_answer_accepts_single_answer_string_for_compatibility():
    generated = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": "answer-string-session",
            "inputType": "text",
            "content": "learn ports",
            "questionCount": 5,
        },
    ).json()["data"]
    first_question = generated["questions"][0]
    correct_answer = stored_answer(generated["quizId"], first_question["id"])
    wrong_answer = "B" if correct_answer != ["B"] else "A"

    response = client.post(
        "/api/submit-answer",
        json={
            "sessionId": "answer-string-session",
            "quizId": generated["quizId"],
            "questionId": first_question["id"],
            "answer": wrong_answer,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["isCorrect"] is False
    assert body["data"]["correctAnswer"] == correct_answer


def test_generate_report_after_answers():
    generated = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": "report-session",
            "inputType": "text",
            "content": "学习构建产物是什么",
            "questionCount": 5,
        },
    ).json()["data"]

    for question in generated["questions"]:
        client.post(
            "/api/submit-answer",
            json={
                "sessionId": "report-session",
                "quizId": generated["quizId"],
                "questionId": question["id"],
                "answer": stored_answer(generated["quizId"], question["id"]),
            },
        )

    response = client.post(
        "/api/generate-report",
        json={"sessionId": "report-session", "quizId": generated["quizId"]},
    )

    assert response.status_code == 200
    body = response.json()
    report = body["data"]
    assert body["code"] == 0
    assert report["score"] == 5
    assert report["total"] == 5
    assert report["mastery"] == 100
    assert report["summary"]
    assert report["nextSteps"]


def test_wrong_questions_history_daily_profile_and_weak_regeneration():
    session_id = "iteration-session"
    generated = client.post(
        "/api/generate-quiz",
        json={
            "sessionId": session_id,
            "inputType": "text",
            "content": "学习端口、数据库和 Redis",
            "questionCount": 5,
        },
    ).json()["data"]
    first_question = generated["questions"][0]
    correct_answer = stored_answer(generated["quizId"], first_question["id"])
    wrong_answer = ["B"] if correct_answer != ["B"] else ["A"]

    wrong_response = client.post(
        "/api/submit-answer",
        json={
            "sessionId": session_id,
            "quizId": generated["quizId"],
            "questionId": first_question["id"],
            "answer": wrong_answer,
        },
    )
    assert wrong_response.status_code == 200
    assert wrong_response.json()["data"]["isCorrect"] is False

    wrong_questions = client.get(
        "/api/wrong-questions", params={"sessionId": session_id}
    ).json()["data"]
    assert len(wrong_questions) == 1
    assert wrong_questions[0]["questionId"] == first_question["id"]

    client.post(
        "/api/submit-answer",
        json={
            "sessionId": session_id,
            "quizId": generated["quizId"],
            "questionId": first_question["id"],
            "answer": correct_answer,
        },
    )
    wrong_questions_after_review = client.get(
        "/api/wrong-questions", params={"sessionId": session_id}
    ).json()["data"]
    assert wrong_questions_after_review == []

    for question in generated["questions"][1:]:
        client.post(
            "/api/submit-answer",
            json={
                "sessionId": session_id,
                "quizId": generated["quizId"],
                "questionId": question["id"],
                "answer": stored_answer(generated["quizId"], question["id"]),
            },
        )

    report = client.post(
        "/api/generate-report",
        json={"sessionId": session_id, "quizId": generated["quizId"]},
    ).json()["data"]
    assert report["mastery"] == 100

    history = client.get(
        "/api/report-history", params={"sessionId": session_id}
    ).json()["data"]
    assert len(history) >= 1
    assert history[0]["quizId"] == generated["quizId"]

    challenge = client.get(
        "/api/daily-challenge", params={"sessionId": session_id}
    ).json()["data"]
    assert challenge["target"] == 5
    assert challenge["answered"] == 5
    assert challenge["completed"] is True

    profile = client.get("/api/profile", params={"sessionId": session_id}).json()["data"]
    assert profile["totalAnswered"] >= 5
    assert profile["exp"] > 0
    assert any(badge["id"] == "first-quiz" and badge["unlocked"] for badge in profile["badges"])
    assert any(badge["id"] == "perfect-run" and badge["unlocked"] for badge in profile["badges"])

    regenerated = client.post(
        "/api/regenerate-weak-quiz",
        json={"sessionId": session_id, "quizId": generated["quizId"]},
    ).json()["data"]
    assert regenerated["quizId"]
    assert len(regenerated["questions"]) == 5
