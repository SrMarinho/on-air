from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from onair.core.errors import ConflictError, DomainError, NotFoundError


class RoomStatus(StrEnum):
    LOBBY = "lobby"
    PLAYING = "playing"


@dataclass(slots=True)
class RoomMember:
    player_id: UUID
    username: str
    ready: bool = False


class NotHostError(DomainError):
    code = "not_host"
    status_code = 403


@dataclass(slots=True)
class Room:
    name: str
    max_players: int
    id: UUID = field(default_factory=uuid4)
    status: RoomStatus = RoomStatus.LOBBY
    host_id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _members: dict[UUID, RoomMember] = field(default_factory=dict)

    @property
    def members(self) -> list[RoomMember]:
        return list(self._members.values())

    @property
    def is_empty(self) -> bool:
        return not self._members

    def has_member(self, player_id: UUID) -> bool:
        return player_id in self._members

    def join(self, player_id: UUID, username: str) -> None:
        if player_id in self._members:
            return
        if self.status is not RoomStatus.LOBBY:
            raise ConflictError("Match already in progress")
        if len(self._members) >= self.max_players:
            raise ConflictError("Room is full")
        self._members[player_id] = RoomMember(player_id, username)
        if self.host_id is None:
            self.host_id = player_id

    def leave(self, player_id: UUID) -> None:
        self._members.pop(player_id, None)
        if self.host_id == player_id:
            self.host_id = next(iter(self._members), None)

    def set_ready(self, player_id: UUID, ready: bool) -> None:
        self._member(player_id).ready = ready

    def start(self, requested_by: UUID) -> None:
        if requested_by != self.host_id:
            raise NotHostError("Only the host can start the match")
        if self.status is not RoomStatus.LOBBY:
            raise ConflictError("Match already in progress")
        not_ready = [m for m in self.members if not m.ready and m.player_id != self.host_id]
        if not_ready:
            raise ConflictError("Not every player is ready")
        self.status = RoomStatus.PLAYING

    def back_to_lobby(self) -> None:
        self.status = RoomStatus.LOBBY
        for member in self._members.values():
            member.ready = False

    def _member(self, player_id: UUID) -> RoomMember:
        member = self._members.get(player_id)
        if member is None:
            raise NotFoundError("Player is not in this room")
        return member
