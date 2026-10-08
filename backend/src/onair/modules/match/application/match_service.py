import logging
from collections.abc import Awaitable, Callable
from uuid import UUID

from onair.core.errors import NotFoundError
from onair.core.ports import Broadcaster
from onair.modules.match.application.match_loop import MatchLoop
from onair.modules.match.application.ports import MatchResultRecorder
from onair.modules.match.application.presenter import MatchPresenter
from onair.modules.match.application.session_factory import SessionFactory
from onair.modules.match.domain.session import GameSession
from onair.modules.rooms.application.ports import MatchPort
from onair.modules.rooms.domain.room import Room

logger = logging.getLogger(__name__)

RoomFinishedCallback = Callable[[UUID], Awaitable[None]]


class MatchService(MatchPort):
    """Owns one `MatchLoop` per playing room and routes player commands to its session."""

    def __init__(
        self,
        factory: SessionFactory,
        broadcaster: Broadcaster,
        recorder: MatchResultRecorder,
        simulation_hz: int,
        snapshot_hz: int,
    ) -> None:
        self._factory = factory
        self._broadcaster = broadcaster
        self._recorder = recorder
        self._presenter = MatchPresenter(simulation_hz)
        self._simulation_hz = simulation_hz
        self._snapshot_hz = snapshot_hz
        self._loops: dict[UUID, MatchLoop] = {}
        self._room_of_player: dict[UUID, UUID] = {}
        self._on_room_finished: RoomFinishedCallback | None = None

    def on_room_finished(self, callback: RoomFinishedCallback) -> None:
        self._on_room_finished = callback

    async def start_match(self, room: Room) -> None:
        session = self._factory.create([(m.player_id, m.username) for m in room.members])
        loop = MatchLoop(
            room_id=room.id,
            session=session,
            broadcaster=self._broadcaster,
            presenter=self._presenter,
            simulation_hz=self._simulation_hz,
            snapshot_hz=self._snapshot_hz,
            on_finished=self._finished,
        )
        self._loops[room.id] = loop
        for member in room.members:
            self._room_of_player[member.player_id] = room.id
        loop.start()

    async def remove_player(self, room_id: UUID, player_id: UUID) -> None:
        self._room_of_player.pop(player_id, None)
        loop = self._loops.get(room_id)
        if loop is not None:
            loop.session.remove_player(player_id)

    def session_for(self, player_id: UUID) -> GameSession:
        room_id = self._room_of_player.get(player_id)
        loop = self._loops.get(room_id) if room_id else None
        if loop is None:
            raise NotFoundError("You are not in a match")
        return loop.session

    async def shutdown(self) -> None:
        for loop in list(self._loops.values()):
            await loop.stop()
        self._loops.clear()

    async def _finished(self, room_id: UUID, session: GameSession) -> None:
        self._loops.pop(room_id, None)
        participants = list(session.context.participants)
        for player_id in participants:
            self._room_of_player.pop(player_id, None)
        ranked = sorted(session.context.participants.values(), key=lambda p: -p.score)
        winner = ranked[0].player_id if ranked and ranked[0].score > 0 else None
        try:
            await self._recorder.record(participants, winner)
        except Exception:
            logger.exception("Failed to record results for room %s", room_id)
        if self._on_room_finished is not None:
            await self._on_room_finished(room_id)
