import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from uuid import UUID

from onair.core.ports import Broadcaster
from onair.modules.match.application.presenter import MatchPresenter
from onair.modules.match.domain.session import GameSession
from onair.protocol.base import Message

logger = logging.getLogger(__name__)

MAX_CATCH_UP_STEPS = 5

FinishedCallback = Callable[[UUID, GameSession], Awaitable[None]]


class MatchLoop:
    """Fixed-timestep driver: simulates at `simulation_hz`, broadcasts at `snapshot_hz`."""

    def __init__(
        self,
        room_id: UUID,
        session: GameSession,
        broadcaster: Broadcaster,
        presenter: MatchPresenter,
        simulation_hz: int,
        snapshot_hz: int,
        on_finished: FinishedCallback,
    ) -> None:
        self._room_id = room_id
        self._session = session
        self._broadcaster = broadcaster
        self._presenter = presenter
        self._dt = 1.0 / simulation_hz
        self._snapshot_every = max(1, simulation_hz // snapshot_hz)
        self._on_finished = on_finished
        self._task: asyncio.Task[None] | None = None

    @property
    def session(self) -> GameSession:
        return self._session

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name=f"match-{self._room_id}")

    async def stop(self) -> None:
        if self._task is not None and not self._task.done():
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        try:
            await self._broadcast(self._presenter.match_started(self._session))
            self._session.start()
            next_step = loop.time()
            while not self._session.finished:
                steps = 0
                while loop.time() >= next_step and steps < MAX_CATCH_UP_STEPS:
                    self._session.update(self._dt)
                    next_step += self._dt
                    steps += 1
                    if self._session.tick % self._snapshot_every == 0:
                        await self._broadcast(self._presenter.snapshot(self._session))
                if steps == MAX_CATCH_UP_STEPS:
                    next_step = loop.time()  # fell behind: drop time instead of spiralling
                await self._flush_notifications()
                await asyncio.sleep(max(0.0, next_step - loop.time()))
            await self._flush_notifications()
            await self._on_finished(self._room_id, self._session)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Match loop for room %s crashed", self._room_id)

    async def _flush_notifications(self) -> None:
        for notification in self._session.drain_notifications():
            await self._broadcast(self._presenter.notification(self._session, notification))

    async def _broadcast(self, message: Message) -> None:
        await self._broadcaster.send_to_room(self._room_id, message)
