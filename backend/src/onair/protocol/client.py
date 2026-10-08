from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, TypeAdapter

from onair.protocol.base import Message


class AuthMessage(Message):
    type: Literal["auth"] = "auth"
    token: str


class JoinRoomMessage(Message):
    type: Literal["join_room"] = "join_room"
    room_id: UUID


class LeaveRoomMessage(Message):
    type: Literal["leave_room"] = "leave_room"


class SetReadyMessage(Message):
    type: Literal["set_ready"] = "set_ready"
    ready: bool


class StartMatchMessage(Message):
    type: Literal["start_match"] = "start_match"


class InputMessage(Message):
    type: Literal["input"] = "input"
    seq: int = Field(ge=0)
    left: bool = False
    right: bool = False
    jump: bool = False


class PickItemMessage(Message):
    type: Literal["pick_item"] = "pick_item"
    offer_id: int = Field(ge=0)


class PlaceItemMessage(Message):
    type: Literal["place_item"] = "place_item"
    tile_x: int
    tile_y: int


class PingMessage(Message):
    type: Literal["ping"] = "ping"
    client_time: float


ClientMessage = Annotated[
    AuthMessage
    | JoinRoomMessage
    | LeaveRoomMessage
    | SetReadyMessage
    | StartMatchMessage
    | InputMessage
    | PickItemMessage
    | PlaceItemMessage
    | PingMessage,
    Field(discriminator="type"),
]

client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)
