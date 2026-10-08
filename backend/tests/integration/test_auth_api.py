from fastapi.testclient import TestClient

from tests.integration.conftest import register


def test_register_login_and_profile(client: TestClient) -> None:
    register(client, "alice")

    login = client.post("/auth/login", json={"username": "alice", "password": "supersecret"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/players/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "alice"


def test_duplicate_username_conflicts(client: TestClient) -> None:
    register(client, "bob")
    response = client.post(
        "/auth/register",
        json={"username": "bob", "email": "other@test.dev", "password": "supersecret"},
    )
    assert response.status_code == 409


def test_wrong_password_is_unauthorized(client: TestClient) -> None:
    register(client, "carol")
    response = client.post("/auth/login", json={"username": "carol", "password": "nope-nope"})
    assert response.status_code == 401


def test_refresh_issues_new_tokens(client: TestClient) -> None:
    tokens = register(client, "dave")
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    assert response.json()["player_id"] == tokens["player_id"]


def test_profile_requires_token(client: TestClient) -> None:
    assert client.get("/players/me").status_code == 401
