import random
from dataclasses import dataclass, field
from uuid import UUID

from onair.ecs import Entity, Scheduler, World
from onair.modules.match.domain.items import ItemRegistry
from onair.modules.match.domain.level_builder import LevelRuntime
from onair.modules.match.domain.notifications import Notification
from onair.modules.match.domain.physics import PhysicsConfig
from onair.modules.match.domain.scoring import ScoringRules


@dataclass(frozen=True, slots=True)
class MatchRules:
    pick_seconds: float = 15.0
    place_seconds: float = 20.0
    run_seconds: float = 60.0
    score_seconds: float = 4.0
    scoring: ScoringRules = field(default_factory=ScoringRules)


@dataclass(slots=True)
class Participant:
    player_id: UUID
    username: str
    color: int
    score: int = 0
    connected: bool = True
    held_item: str | None = None
    entity: Entity | None = None
    last_input_seq: int = 0


@dataclass(slots=True)
class MatchContext:
    """Everything a phase may touch. Phases are the only writers of match-level state."""

    world: World
    scheduler: Scheduler
    level: LevelRuntime
    items: ItemRegistry
    physics: PhysicsConfig
    rules: MatchRules
    rng: random.Random
    participants: dict[UUID, Participant]
    round: int = 1
    notifications: list[Notification] = field(default_factory=list)

    def active(self) -> list[Participant]:
        return [p for p in self.participants.values() if p.connected]

    def notify(self, notification: Notification) -> None:
        self.notifications.append(notification)
