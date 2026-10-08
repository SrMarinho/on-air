from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, TypeAdapter

from onair.protocol.base import Message


class AuthOkMessage(Message):
    type: Literal["auth_ok"] = "auth_ok"
    player_id: UUID
    username: str


class ErrorMessage(Message):
    type: Literal["error"] = "error"
    code: str
    message: str


class RoomMember(Message):
    player_id: UUID
    username: str
    ready: bool
    is_host: bool


class RoomStateMessage(Message):
    type: Literal["room_state"] = "room_state"
    room_id: UUID
    name: str
    status: Literal["lobby", "playing", "finished"]
    max_players: int
    members: list[RoomMember]


class LevelLayout(Message):
    key: str
    width: int
    height: int
    tile_size: int
    rows: list[str]


class MatchPlayer(Message):
    player_id: UUID
    username: str
    color: int


class MatchStartedMessage(Message):
    type: Literal["match_started"] = "match_started"
    level: LevelLayout
    players: list[MatchPlayer]
    target_score: int
    simulation_hz: int


class ItemOffer(Message):
    offer_id: int
    item: str
    taken_by: UUID | None = None


class ScoreLine(Message):
    player_id: UUID
    total: int
    gained: int
    reasons: list[str]


class PhaseChangedMessage(Message):
    type: Literal["phase_changed"] = "phase_changed"
    phase: Literal["pick", "place", "run", "score", "end"]
    round: int
    duration: float
    offers: list[ItemOffer] | None = None
    scores: list[ScoreLine] | None = None


class ItemPickedMessage(Message):
    type: Literal["item_picked"] = "item_picked"
    player_id: UUID
    offer_id: int
    item: str


class EntityState(Message):
    id: int
    kind: str
    x: float
    y: float
    w: float
    h: float
    vx: float = 0.0
    vy: float = 0.0
    player_id: UUID | None = None
    state: Literal["alive", "dead", "finished"] | None = None


class SnapshotMessage(Message):
    type: Literal["snapshot"] = "snapshot"
    tick: int
    phase_time_left: float
    acks: dict[str, int]
    entities: list[EntityState]


class LevelItemsMessage(Message):
    """Full list of placed static items; sent whenever it changes."""

    type: Literal["level_items"] = "level_items"
    items: list[EntityState]


class MatchEndedMessage(Message):
    type: Literal["match_ended"] = "match_ended"
    winner_id: UUID | None
    scores: list[ScoreLine]


class PongMessage(Message):
    type: Literal["pong"] = "pong"
    client_time: float
    server_time: float


ServerMessage = Annotated[
    AuthOkMessage
    | ErrorMessage
    | RoomStateMessage
    | MatchStartedMessage
    | PhaseChangedMessage
    | ItemPickedMessage
    | SnapshotMessage
    | LevelItemsMessage
    | MatchEndedMessage
    | PongMessage,
    Field(discriminator="type"),
]

server_message_adapter: TypeAdapter[ServerMessage] = TypeAdapter(ServerMessage)
