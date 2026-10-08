import asyncio
import logging
from collections.abc import Sequence

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from onair.core.errors import DomainError, UnauthorizedError
from onair.gateway.connection import ClientConnection, Identity
from onair.gateway.connection_manager import ConnectionManager
from onair.gateway.dispatcher import Dispatcher, UnknownMessageError
from onair.gateway.ports import Authenticator, DisconnectListener
from onair.protocol.client import AuthMessage, client_message_adapter
from onair.protocol.server import AuthOkMessage, ErrorMessage

logger = logging.getLogger(__name__)

AUTH_TIMEOUT_SECONDS = 10.0
POLICY_VIOLATION = 1008


class GameSocketEndpoint:
    """WebSocket lifecycle: authenticate → register → receive/dispatch loop → cleanup."""

    def __init__(
        self,
        manager: ConnectionManager,
        dispatcher: Dispatcher,
        authenticator: Authenticator,
        disconnect_listeners: Sequence[DisconnectListener] = (),
    ) -> None:
        self._manager = manager
        self._dispatcher = dispatcher
        self._authenticator = authenticator
        self._disconnect_listeners = list(disconnect_listeners)

    def router(self, path: str = "/ws") -> APIRouter:
        router = APIRouter()
        router.add_api_websocket_route(path, self.serve)
        return router

    async def serve(self, websocket: WebSocket) -> None:
        await websocket.accept()
        identity = await self._authenticate(websocket)
        if identity is None:
            return
        connection = ClientConnection(websocket, identity)
        previous = self._manager.register(connection)
        if previous is not None:
            await previous.close(close_socket=True)
        connection.start()
        connection.send(AuthOkMessage(player_id=identity.player_id, username=identity.username))
        try:
            await self._receive_loop(websocket, connection)
        except WebSocketDisconnect:
            pass
        finally:
            await connection.close()
            if self._manager.unregister(connection):
                for listener in self._disconnect_listeners:
                    await listener.on_disconnect(connection)

    async def _authenticate(self, websocket: WebSocket) -> Identity | None:
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), AUTH_TIMEOUT_SECONDS)
            message = AuthMessage.model_validate_json(raw)
            return await self._authenticator.authenticate(message.token)
        except (TimeoutError, ValidationError, UnauthorizedError, WebSocketDisconnect):
            await websocket.close(code=POLICY_VIOLATION)
            return None

    async def _receive_loop(self, websocket: WebSocket, connection: ClientConnection) -> None:
        while True:
            raw = await websocket.receive_text()
            try:
                message = client_message_adapter.validate_json(raw)
                await self._dispatcher.dispatch(connection, message)
            except ValidationError as exc:
                connection.send(ErrorMessage(code="invalid_message", message=str(exc.errors()[0])))
            except UnknownMessageError as exc:
                connection.send(ErrorMessage(code="unsupported_message", message=str(exc)))
            except DomainError as exc:
                connection.send(ErrorMessage(code=exc.code, message=exc.message))
