from datetime import UTC, datetime, timedelta
from uuid import UUID

from onair.core.errors import NotFoundError
from onair.core.ports import Broadcaster
from onair.modules.rooms.application.ports import MatchPort
from onair.modules.rooms.domain.repository import RoomRepository
from onair.modules.rooms.domain.room import Room, RoomStatus
from onair.protocol.server import RoomMember as RoomMemberMessage
from onair.protocol.server import RoomStateMessage

EMPTY_ROOM_GRACE = timedelta(minutes=2)


class RoomService:
    def __init__(
        self,
        rooms: RoomRepository,
        broadcaster: Broadcaster,
        matches: MatchPort,
        max_players: int,
    ) -> None:
        self._rooms = rooms
        self._broadcaster = broadcaster
        self._matches = matches
        self._max_players = max_players
        self._player_room: dict[UUID, UUID] = {}

    def create(self, name: str) -> Room:
        room = Room(name=name, max_players=self._max_players)
        self._rooms.add(room)
        return room

    def list_open(self) -> list[Room]:
        self._prune_abandoned()
        return [r for r in self._rooms.all() if r.status is RoomStatus.LOBBY]

    def get(self, room_id: UUID) -> Room:
        room = self._rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        return room

    def room_of(self, player_id: UUID) -> Room | None:
        room_id = self._player_room.get(player_id)
        return self._rooms.get(room_id) if room_id else None

    async def join(self, room_id: UUID, player_id: UUID, username: str) -> Room:
        current = self.room_of(player_id)
        if current is not None and current.id != room_id:
            await self.leave(player_id)
        room = self.get(room_id)
        room.join(player_id, username)
        self._player_room[player_id] = room.id
        self._broadcaster.bind_room(player_id, room.id)
        await self._publish(room)
        return room

    async def leave(self, player_id: UUID) -> None:
        room = self.room_of(player_id)
        self._player_room.pop(player_id, None)
        self._broadcaster.bind_room(player_id, None)
        if room is None:
            return
        room.leave(player_id)
        if room.status is RoomStatus.PLAYING:
            await self._matches.remove_player(room.id, player_id)
        if room.is_empty:
            self._rooms.remove(room.id)
            return
        await self._publish(room)

    async def set_ready(self, player_id: UUID, ready: bool) -> None:
        room = self._require_room_of(player_id)
        room.set_ready(player_id, ready)
        await self._publish(room)

    async def start_match(self, player_id: UUID) -> None:
        room = self._require_room_of(player_id)
        room.start(player_id)
        await self._publish(room)
        await self._matches.start_match(room)

    async def match_finished(self, room_id: UUID) -> None:
        room = self._rooms.get(room_id)
        if room is None:
            return
        room.back_to_lobby()
        await self._publish(room)

    def _require_room_of(self, player_id: UUID) -> Room:
        room = self.room_of(player_id)
        if room is None:
            raise NotFoundError("You are not in a room")
        return room

    def _prune_abandoned(self) -> None:
        cutoff = datetime.now(UTC) - EMPTY_ROOM_GRACE
        for room in self._rooms.all():
            if room.is_empty and room.created_at < cutoff:
                self._rooms.remove(room.id)

    async def _publish(self, room: Room) -> None:
        await self._broadcaster.send_to_room(room.id, to_room_state(room))


def to_room_state(room: Room) -> RoomStateMessage:
    return RoomStateMessage(
        room_id=room.id,
        name=room.name,
        status=room.status.value,
        max_players=room.max_players,
        members=[
            RoomMemberMessage(
                player_id=m.player_id,
                username=m.username,
                ready=m.ready,
                is_host=m.player_id == room.host_id,
            )
            for m in room.members
        ],
    )
