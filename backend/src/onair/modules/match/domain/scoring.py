from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ScoringRules:
    goal: int = 2  # CHEGOU
    first: int = 1  # PRIMEIRO A CHEGAR
    solo: int = 1  # EXCLUSIVA!
    target: int = 12


@dataclass(slots=True)
class RoundScore:
    player_id: UUID
    gained: int = 0
    reasons: list[str] = field(default_factory=list)

    def award(self, points: int, reason: str) -> None:
        self.gained += points
        self.reasons.append(reason)


class RoundScorer:
    """Audience meter (design system §15.9): nobody scores if everybody (or nobody) made it."""

    def __init__(self, rules: ScoringRules) -> None:
        self._rules = rules

    def score(self, participants: list[UUID], finish_order: list[UUID]) -> list[RoundScore]:
        scores = {pid: RoundScore(pid) for pid in participants}
        finishers = [pid for pid in finish_order if pid in scores]
        multiplayer = len(participants) > 1
        if not finishers or (multiplayer and len(finishers) == len(participants)):
            return list(scores.values())
        for pid in finishers:
            scores[pid].award(self._rules.goal, "goal")
        if multiplayer:
            scores[finishers[0]].award(self._rules.first, "first")
        if multiplayer and len(finishers) == 1:
            scores[finishers[0]].award(self._rules.solo, "solo")
        return list(scores.values())
