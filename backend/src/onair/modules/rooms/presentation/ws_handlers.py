from onair.gateway.connection import ClientConnection
from onair.gateway.dispatcher import Dispatcher, MessageHandler
from onair.gateway.ports import DisconnectListener
from onair.modules.rooms.application.room_service import RoomService
from onair.protocol.client import (
    JoinRoomMessage,
    LeaveRoomMessage,
    SetReadyMessage,
    StartMatchMessage,
)


class JoinRoomHandler(MessageHandler[JoinRoomMessage]):
    message_type = JoinRoomMessage

    def __init__(self, rooms: RoomService) -> None:
        self._rooms = rooms

    async def handle(self, connection: ClientConnection, message: JoinRoomMessage) -> None:
        await self._rooms.join(message.room_id, connection.player_id, connection.identity.username)


class LeaveRoomHandler(MessageHandler[LeaveRoomMessage]):
    message_type = LeaveRoomMessage

    def __init__(self, rooms: RoomService) -> None:
        self._rooms = rooms

    async def handle(self, connection: ClientConnection, message: LeaveRoomMessage) -> None:
        await self._rooms.leave(connection.player_id)


class SetReadyHandler(MessageHandler[SetReadyMessage]):
    message_type = SetReadyMessage

    def __init__(self, rooms: RoomService) -> None:
        self._rooms = rooms

    async def handle(self, connection: ClientConnection, message: SetReadyMessage) -> None:
        await self._rooms.set_ready(connection.player_id, message.ready)


class StartMatchHandler(MessageHandler[StartMatchMessage]):
    message_type = StartMatchMessage

    def __init__(self, rooms: RoomService) -> None:
        self._rooms = rooms

    async def handle(self, connection: ClientConnection, message: StartMatchMessage) -> None:
        await self._rooms.start_match(connection.player_id)


class LeaveRoomOnDisconnect(DisconnectListener):
    def __init__(self, rooms: RoomService) -> None:
        self._rooms = rooms

    async def on_disconnect(self, connection: ClientConnection) -> None:
        await self._rooms.leave(connection.player_id)


def register_room_handlers(dispatcher: Dispatcher, rooms: RoomService) -> None:
    dispatcher.register(JoinRoomHandler(rooms))
    dispatcher.register(LeaveRoomHandler(rooms))
    dispatcher.register(SetReadyHandler(rooms))
    dispatcher.register(StartMatchHandler(rooms))
