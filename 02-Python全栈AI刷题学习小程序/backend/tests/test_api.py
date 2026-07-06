from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_service_status():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["status"] == "running"
    assert body["data"]["product"] == "水母diy学习助手"


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
        assert question["answer"]
        assert question["explanation"]
        assert question["knowledge_point"]
        assert question["difficulty"] in {"easy", "medium", "hard"}


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


def test_generate_quiz_from_assets_accepts_text_files_and_images():
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

    response = client.post(
        "/api/submit-answer",
        json={
            "sessionId": "answer-session",
            "quizId": generated["quizId"],
            "questionId": first_question["id"],
            "answer": first_question["answer"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["isCorrect"] is True
    assert body["data"]["correctAnswer"] == first_question["answer"]
    assert body["data"]["explanation"]


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
                "answer": question["answer"],
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
    wrong_answer = ["B"] if first_question["answer"] != ["B"] else ["A"]

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
            "answer": first_question["answer"],
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
                "answer": question["answer"],
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
