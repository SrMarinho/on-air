"""Round flow as a State machine: Pick → Place → Run → Score → (Pick | End)."""

from abc import ABC, abstractmethod
from typing import ClassVar
from uuid import UUID

from onair.core.errors import DomainError
from onair.modules.match.domain.components import (
    Body,
    Collider,
    Contacts,
    Goal,
    Hazard,
    PlayerInput,
    PlayerTag,
    Renderable,
    Solid,
    Transform,
    Velocity,
)
from onair.modules.match.domain.context import MatchContext, Participant
from onair.modules.match.domain.events import PlayerReachedGoal
from onair.modules.match.domain.notifications import (
    ItemPicked,
    MatchFinished,
    Offer,
    PhaseName,
    PhaseStarted,
    ScoreEntry,
    StaticsChanged,
)
from onair.modules.match.domain.physics import Rect, rect_of
from onair.modules.match.domain.scoring import RoundScore, RoundScorer


class PhaseRuleError(DomainError):
    code = "not_allowed"


class Phase(ABC):
    name: ClassVar[PhaseName]

    def __init__(self, ctx: MatchContext, duration: float) -> None:
        self._ctx = ctx
        self.duration = duration
        self.time_left = duration

    def enter(self) -> None:
        self._ctx.notify(PhaseStarted(self.name, self._ctx.round, self.duration))

    def exit(self) -> None:
        """Hook for cleanup when leaving the phase."""

    def tick(self, dt: float) -> "Phase | None":
        self.time_left = max(0.0, self.time_left - dt)
        self.on_tick(dt)
        if self.is_complete() or self.time_left <= 0.0:
            return self.next_phase()
        return None

    def on_tick(self, dt: float) -> None:
        """Hook for per-tick work."""

    @abstractmethod
    def is_complete(self) -> bool: ...

    @abstractmethod
    def next_phase(self) -> "Phase | None": ...

    def pick(self, player_id: UUID, offer_id: int) -> None:
        raise PhaseRuleError("Cannot pick an item now")

    def place(self, player_id: UUID, tile_x: int, tile_y: int) -> None:
        raise PhaseRuleError("Cannot place an item now")

    def participant_left(self, participant: Participant) -> None:
        """Hook for phases holding per-player state."""


class PickPhase(Phase):
    name = "pick"

    def __init__(self, ctx: MatchContext) -> None:
        super().__init__(ctx, ctx.rules.pick_seconds)
        keys = ctx.items.draw(ctx.rng, len(ctx.active()) + 1)
        self._offers = [Offer(i, key) for i, key in enumerate(keys)]

    @property
    def offers(self) -> tuple[Offer, ...]:
        return tuple(self._offers)

    def enter(self) -> None:
        for participant in self._ctx.participants.values():
            participant.held_item = None
        self._ctx.notify(
            PhaseStarted(self.name, self._ctx.round, self.duration, offers=self.offers)
        )

    def pick(self, player_id: UUID, offer_id: int) -> None:
        participant = self._ctx.participants[player_id]
        if participant.held_item is not None:
            raise PhaseRuleError("You already picked an item")
        if not 0 <= offer_id < len(self._offers) or self._offers[offer_id].taken_by:
            raise PhaseRuleError("Item not available")
        self._take(participant, offer_id)

    def is_complete(self) -> bool:
        return all(p.held_item is not None for p in self._ctx.active())

    def next_phase(self) -> Phase:
        for participant in self._ctx.active():
            if participant.held_item is None:
                free = [o.offer_id for o in self._offers if o.taken_by is None]
                self._take(participant, self._ctx.rng.choice(free))
        return PlacePhase(self._ctx)

    def _take(self, participant: Participant, offer_id: int) -> None:
        offer = self._offers[offer_id]
        self._offers[offer_id] = Offer(offer.offer_id, offer.item, participant.player_id)
        participant.held_item = offer.item
        self._ctx.notify(ItemPicked(participant.player_id, offer_id, offer.item))


class PlacePhase(Phase):
    name = "place"

    def __init__(self, ctx: MatchContext) -> None:
        super().__init__(ctx, ctx.rules.place_seconds)

    def place(self, player_id: UUID, tile_x: int, tile_y: int) -> None:
        participant = self._ctx.participants[player_id]
        if participant.held_item is None:
            raise PhaseRuleError("You have no item to place")
        item = self._ctx.items.get(participant.held_item)
        tile_size = self._ctx.level.definition.tile_size
        area = item.footprint(tile_x, tile_y, tile_size)
        bounds = self._ctx.level.bounds
        inside = (
            area.x >= bounds.x
            and area.y >= bounds.y
            and area.right <= bounds.right
            and area.bottom <= bounds.bottom
        )
        if not inside:
            raise PhaseRuleError("Item must be inside the level")
        if item.requires_free_space and (
            any(area.overlaps(zone) for zone in self._ctx.level.keep_out) or self._blocked(area)
        ):
            raise PhaseRuleError("That spot is occupied")
        item.place(self._ctx.world, area, player_id, tile_size)
        self._ctx.world.flush()
        participant.held_item = None
        self._ctx.notify(StaticsChanged())

    def _blocked(self, area: Rect) -> bool:
        world = self._ctx.world
        occupied = [e for e, _ in world.query(Solid)]
        occupied += [e for e, _ in world.query(Hazard)]
        occupied += [e for e, _ in world.query(Goal)]
        return any(rect_of(world, e).overlaps(area) for e in occupied)

    def is_complete(self) -> bool:
        return all(p.held_item is None for p in self._ctx.active())

    def next_phase(self) -> Phase:
        return RunPhase(self._ctx)

    def exit(self) -> None:
        for participant in self._ctx.participants.values():
            participant.held_item = None


class RunPhase(Phase):
    name = "run"

    def __init__(self, ctx: MatchContext) -> None:
        super().__init__(ctx, ctx.rules.run_seconds)
        self._finish_order: list[UUID] = []

    def enter(self) -> None:
        super().enter()
        spawns = self._ctx.level.spawns
        for index, participant in enumerate(self._ctx.active()):
            self._spawn(participant, spawns[index % len(spawns)])

    def on_tick(self, dt: float) -> None:
        world = self._ctx.world
        self._ctx.scheduler.tick(world, dt)
        self._finish_order.extend(e.player_id for e in world.events.read(PlayerReachedGoal))
        world.events.clear()

    def is_complete(self) -> bool:
        world = self._ctx.world
        return all(
            p.entity is None or not world.require(p.entity, PlayerTag).alive
            for p in self._ctx.active()
        )

    def next_phase(self) -> Phase:
        return ScorePhase(self._ctx, self._finish_order)

    def exit(self) -> None:
        for participant in self._ctx.participants.values():
            if participant.entity is not None:
                self._ctx.world.destroy_entity(participant.entity)
                participant.entity = None
        self._ctx.world.flush()

    def participant_left(self, participant: Participant) -> None:
        if participant.entity is not None:
            self._ctx.world.destroy_entity(participant.entity)
            self._ctx.world.flush()
            participant.entity = None

    def _spawn(self, participant: Participant, spawn: tuple[float, float]) -> None:
        cfg = self._ctx.physics
        tile = self._ctx.level.definition.tile_size
        participant.entity = self._ctx.world.create_entity(
            Transform(
                spawn[0] + (tile - cfg.player_width) / 2, spawn[1] + tile - cfg.player_height
            ),
            Velocity(),
            Collider(cfg.player_width, cfg.player_height),
            Body(),
            Contacts(),
            PlayerInput(last_seq=participant.last_input_seq),
            PlayerTag(participant.player_id),
            Renderable("player"),
        )


class ScorePhase(Phase):
    name = "score"

    def __init__(self, ctx: MatchContext, finish_order: list[UUID]) -> None:
        super().__init__(ctx, ctx.rules.score_seconds)
        self._finish_order = finish_order
        self._entries: tuple[ScoreEntry, ...] = ()

    def enter(self) -> None:
        scorer = RoundScorer(self._ctx.rules.scoring)
        round_scores = scorer.score([p.player_id for p in self._ctx.active()], self._finish_order)
        for round_score in round_scores:
            self._ctx.participants[round_score.player_id].score += round_score.gained
        self._entries = _entries(self._ctx, round_scores)
        self._ctx.notify(
            PhaseStarted(self.name, self._ctx.round, self.duration, scores=self._entries)
        )

    def is_complete(self) -> bool:
        return False

    def next_phase(self) -> Phase:
        target = self._ctx.rules.scoring.target
        if any(p.score >= target for p in self._ctx.participants.values()):
            return EndPhase(self._ctx)
        self._ctx.round += 1
        return PickPhase(self._ctx)


class EndPhase(Phase):
    name = "end"

    def __init__(self, ctx: MatchContext) -> None:
        super().__init__(ctx, 0.0)

    def enter(self) -> None:
        super().enter()
        entries = _entries(self._ctx, [])
        ranked = sorted(self._ctx.participants.values(), key=lambda p: p.score, reverse=True)
        winner = ranked[0].player_id if ranked and ranked[0].score > 0 else None
        self._ctx.notify(MatchFinished(winner, entries))

    def tick(self, dt: float) -> Phase | None:
        return None

    def is_complete(self) -> bool:
        return True

    def next_phase(self) -> Phase | None:
        return None


def _entries(ctx: MatchContext, round_scores: list[RoundScore]) -> tuple[ScoreEntry, ...]:
    by_player = {rs.player_id: rs for rs in round_scores}
    return tuple(
        ScoreEntry(
            player_id=p.player_id,
            total=p.score,
            gained=by_player[p.player_id].gained if p.player_id in by_player else 0,
            reasons=tuple(by_player[p.player_id].reasons) if p.player_id in by_player else (),
        )
        for p in ctx.participants.values()
    )
