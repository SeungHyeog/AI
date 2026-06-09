from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_selects_incident_triage_by_default() -> None:
    response = client.post("/chat", json={"message": "checkout-api가 느려졌어"})

    assert response.status_code == 200
    assert response.json()["selected_skill"] == "incident-triage"


def test_chat_requires_approval() -> None:
    response = client.post("/chat", json={"message": "이번 PR 배포해도 괜찮아?"})

    assert response.status_code == 200
    body = response.json()
    assert body["selected_skill"] == "deployment-risk-review"
    assert body["requires_approval"] is True
