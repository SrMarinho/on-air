from dataclasses import dataclass
from uuid import UUID

from onair.ecs import Entity
from onair.modules.match.domain.components import (
    Collider,
    PlacedItem,
    PlayerInput,
    PlayerTag,
    Renderable,
    StaticTile,
    Transform,
    Velocity,
)
from onair.modules.match.domain.context import MatchContext
from onair.modules.match.domain.notifications import Notification, PhaseName
from onair.modules.match.domain.phases import EndPhase, Phase, PickPhase


@dataclass(frozen=True, slots=True)
class EntityView:
    id: int
    kind: str
    x: float
    y: float
    w: float
    h: float
    vx: float = 0.0
    vy: float = 0.0
    player_id: UUID | None = None
    state: str | None = None


@dataclass(frozen=True, slots=True)
class SnapshotView:
    tick: int
    phase_time_left: float
    acks: dict[UUID, int]
    entities: list[EntityView]


class GameSession:
    """Synchronous, deterministic match facade. No I/O: the match loop drives it."""

    def __init__(self, ctx: MatchContext) -> None:
        self._ctx = ctx
        self._phase: Phase | None = None
        self.tick = 0

    @property
    def context(self) -> MatchContext:
        return self._ctx

    @property
    def phase_name(self) -> PhaseName | None:
        return self._phase.name if self._phase else None

    @property
    def finished(self) -> bool:
        return isinstance(self._phase, EndPhase)

    def start(self) -> None:
        self._switch(PickPhase(self._ctx))

    def update(self, dt: float) -> None:
        if self._phase is None:
            return
        self.tick += 1
        next_phase = self._phase.tick(dt)
        if next_phase is not None:
            self._switch(next_phase)

    # --- commands -------------------------------------------------------
    def apply_input(self, player_id: UUID, seq: int, left: bool, right: bool, jump: bool) -> None:
        participant = self._ctx.participants.get(player_id)
        if participant is None or seq <= participant.last_input_seq:
            return
        participant.last_input_seq = seq
        if participant.entity is None:
            return
        state = self._ctx.world.get(participant.entity, PlayerInput)
        if state is not None:
            state.left, state.right, state.jump, state.last_seq = left, right, jump, seq

    def pick(self, player_id: UUID, offer_id: int) -> None:
        self._require_phase().pick(player_id, offer_id)

    def place(self, player_id: UUID, tile_x: int, tile_y: int) -> None:
        self._require_phase().place(player_id, tile_x, tile_y)

    def remove_player(self, player_id: UUID) -> None:
        participant = self._ctx.participants.get(player_id)
        if participant is None or not participant.connected:
            return
        participant.connected = False
        participant.held_item = None
        if self._phase is not None:
            self._phase.participant_left(participant)
        if not self._ctx.active() and not self.finished:
            self._switch(EndPhase(self._ctx))

    # --- queries --------------------------------------------------------
    def drain_notifications(self) -> list[Notification]:
        notifications = self._ctx.notifications[:]
        self._ctx.notifications.clear()
        return notifications

    def snapshot(self) -> SnapshotView:
        world = self._ctx.world
        entities = [
            self._view(entity)
            for entity, _, _ in world.query(Renderable, Velocity)
            if not world.has(entity, StaticTile)
        ]
        return SnapshotView(
            tick=self.tick,
            phase_time_left=self._phase.time_left if self._phase else 0.0,
            acks={p.player_id: p.last_input_seq for p in self._ctx.participants.values()},
            entities=entities,
        )

    def statics(self) -> list[EntityView]:
        world = self._ctx.world
        return [
            self._view(entity)
            for entity, _, _ in world.query(Renderable, PlacedItem)
            if not world.has(entity, Velocity)
        ]

    # --- internals ------------------------------------------------------
    def _switch(self, phase: Phase) -> None:
        if self._phase is not None:
            self._phase.exit()
        self._phase = phase
        phase.enter()

    def _require_phase(self) -> Phase:
        if self._phase is None:
            raise RuntimeError("Session not started")
        return self._phase

    def _view(self, entity: Entity) -> EntityView:
        world = self._ctx.world
        transform = world.require(entity, Transform)
        collider = world.require(entity, Collider)
        velocity = world.get(entity, Velocity) or Velocity()
        tag = world.get(entity, PlayerTag)
        return EntityView(
            id=entity,
            kind=world.require(entity, Renderable).kind,
            x=round(transform.x, 2),
            y=round(transform.y, 2),
            w=collider.w,
            h=collider.h,
            vx=round(velocity.vx, 2),
            vy=round(velocity.vy, 2),
            player_id=tag.player_id if tag else None,
            state=tag.state.value if tag else None,
        )
