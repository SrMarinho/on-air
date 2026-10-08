from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PlayerDied:
    player_id: UUID


@dataclass(frozen=True, slots=True)
class PlayerReachedGoal:
    player_id: UUID
