import uuid

from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_board_not_found():
    rand_uuid = uuid.uuid4()
    response = client.get(f"/vote_boards/{rand_uuid}")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_board_getting_scores():
    rand_uuid = uuid.uuid4()
    response = client.get(f"/vote_boards/{rand_uuid}/score")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_board_for_new_idea_not_found():
    rand_uuid = uuid.uuid4()
    response = client.post(
        f"/vote_boards/{rand_uuid}/new_idea",
        json={"board_id": str(rand_uuid), "idea_title": "new", "idea_desc": "none"},
    )
    assert response.status_code == 422


def test_single_idea_get_not_found():
    rand_uuid = uuid.uuid4()
    response = client.get(f"/ideas/{str(rand_uuid)}")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body and body["error"]["code"] == "not_found"
