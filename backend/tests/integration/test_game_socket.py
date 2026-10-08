from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
from starlette.websockets import WebSocketDisconnect

from tests.integration.conftest import register


def _receive_until(ws: WebSocketTestSession, message_type: str, limit: int = 200) -> dict[str, Any]:
    for _ in range(limit):
        message: dict[str, Any] = ws.receive_json()
        if message["type"] == message_type:
            return message
    raise AssertionError(f"Never received {message_type}")


def test_socket_rejects_bad_token(client: TestClient) -> None:
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "token": "garbage"})
        with pytest.raises(WebSocketDisconnect):
            ws.receive_json()


def test_full_flow_auth_join_start_pick_and_snapshot(client: TestClient) -> None:
    tokens = register(client, "host")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    room = client.post("/rooms", json={"name": "Sala"}, headers=headers).json()

    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "token": tokens["access_token"]})
        assert _receive_until(ws, "auth_ok")["username"] == "host"

        ws.send_json({"type": "ping", "client_time": 1.0})
        assert _receive_until(ws, "pong")["client_time"] == 1.0

        ws.send_json({"type": "join_room", "room_id": room["id"]})
        state = _receive_until(ws, "room_state")
        assert state["members"][0]["is_host"] is True

        ws.send_json({"type": "start_match"})
        started = _receive_until(ws, "match_started")
        assert started["level"]["key"] == "meadow"
        pick = _receive_until(ws, "phase_changed")
        assert pick["phase"] == "pick"

        ws.send_json({"type": "pick_item", "offer_id": pick["offers"][0]["offer_id"]})
        assert _receive_until(ws, "item_picked")["player_id"] == tokens["player_id"]
        assert _receive_until(ws, "phase_changed")["phase"] == "place"
        assert "entities" in _receive_until(ws, "snapshot")

        ws.send_json({"type": "pick_item", "offer_id": 0})
        assert _receive_until(ws, "error")["code"] == "not_allowed"


def test_invalid_message_returns_error(client: TestClient) -> None:
    tokens = register(client, "eve")
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "auth", "token": tokens["access_token"]})
        _receive_until(ws, "auth_ok")
        ws.send_json({"type": "input", "seq": -1})
        assert _receive_until(ws, "error")["code"] == "invalid_message"
