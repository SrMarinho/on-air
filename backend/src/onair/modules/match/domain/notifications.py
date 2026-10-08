"""Domain-level outcomes of a tick. The application layer maps them to wire messages."""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

PhaseName = Literal["pick", "place", "run", "score", "end"]


@dataclass(frozen=True, slots=True)
class Offer:
    offer_id: int
    item: str
    taken_by: UUID | None = None


@dataclass(frozen=True, slots=True)
class ScoreEntry:
    player_id: UUID
    total: int
    gained: int
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PhaseStarted:
    phase: PhaseName
    round: int
    duration: float
    offers: tuple[Offer, ...] | None = None
    scores: tuple[ScoreEntry, ...] | None = None


@dataclass(frozen=True, slots=True)
class ItemPicked:
    player_id: UUID
    offer_id: int
    item: str


@dataclass(frozen=True, slots=True)
class StaticsChanged:
    pass


@dataclass(frozen=True, slots=True)
class MatchFinished:
    winner_id: UUID | None
    scores: tuple[ScoreEntry, ...]


Notification = PhaseStarted | ItemPicked | StaticsChanged | MatchFinished
