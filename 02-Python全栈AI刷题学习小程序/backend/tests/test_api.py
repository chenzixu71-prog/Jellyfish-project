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
