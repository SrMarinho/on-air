from uuid import UUID, uuid4

import pytest

from onair.modules.levels.infrastructure.json_repository import JsonLevelRepository
from onair.modules.match.application.session_factory import SessionFactory
from onair.modules.match.domain.context import MatchRules
from onair.modules.match.domain.items import default_item_registry
from onair.modules.match.domain.notifications import ItemPicked, PhaseStarted, StaticsChanged
from onair.modules.match.domain.phases import PhaseRuleError
from onair.modules.match.domain.physics import PhysicsConfig
from onair.modules.match.domain.scoring import RoundScorer, ScoringRules
from onair.modules.match.domain.session import GameSession

DT = 1 / 60


def _session(*players: UUID) -> GameSession:
    factory = SessionFactory(
        JsonLevelRepository(),
        default_item_registry,
        PhysicsConfig(),
        MatchRules(pick_seconds=1, place_seconds=1, run_seconds=1, score_seconds=0.5),
        seed=7,
    )
    return factory.create([(pid, f"p{i}") for i, pid in enumerate(players)])


def _advance(session: GameSession, seconds: float) -> None:
    for _ in range(round(seconds / DT)):
        session.update(DT)


def test_session_starts_in_pick_with_one_extra_offer() -> None:
    a, b = uuid4(), uuid4()
    session = _session(a, b)
    session.start()

    [started] = session.drain_notifications()
    assert isinstance(started, PhaseStarted)
    assert started.phase == "pick"
    assert started.offers is not None and len(started.offers) == 3


def test_full_round_cycles_back_to_pick() -> None:
    a = uuid4()
    session = _session(a)
    session.start()
    session.pick(a, 0)
    seen = []
    for seconds in (DT, 1.1, 1.1, 0.6):
        _advance(session, seconds)
        seen.append(session.phase_name)

    assert seen == ["place", "run", "score", "pick"]
    assert session.context.round == 2


def test_cannot_pick_twice_or_take_taken_offer() -> None:
    a, b = uuid4(), uuid4()
    session = _session(a, b)
    session.start()
    session.pick(a, 0)

    with pytest.raises(PhaseRuleError):
        session.pick(a, 1)
    with pytest.raises(PhaseRuleError):
        session.pick(b, 0)


def test_placing_item_creates_static_and_rejects_occupied_spot() -> None:
    a = uuid4()
    session = _session(a)
    session.start()
    session.pick(a, 0)
    session.update(DT)
    session.drain_notifications()

    session.context.participants[a].held_item = "block"
    session.place(a, 20, 5)

    assert any(isinstance(n, StaticsChanged) for n in session.drain_notifications())
    assert len(session.statics()) == 1
    session.context.participants[a].held_item = "block"
    with pytest.raises(PhaseRuleError):
        session.place(a, 20, 5)


def test_pick_timeout_auto_assigns_items() -> None:
    a, b = uuid4(), uuid4()
    session = _session(a, b)
    session.start()

    _advance(session, 1.1)

    picks = [n for n in session.drain_notifications() if isinstance(n, ItemPicked)]
    assert {p.player_id for p in picks} == {a, b}
    assert session.phase_name == "place"


def test_last_player_leaving_ends_match() -> None:
    a = uuid4()
    session = _session(a)
    session.start()

    session.remove_player(a)

    assert session.finished


def test_run_phase_spawns_players_in_snapshot() -> None:
    a = uuid4()
    session = _session(a)
    session.start()
    session.pick(a, 0)
    session.update(DT)
    session.context.participants[a].held_item = None
    session.update(DT)

    players = [e for e in session.snapshot().entities if e.kind == "player"]
    assert [p.player_id for p in players] == [a]


class TestScoring:
    rules = ScoringRules()

    def test_nobody_scores_when_everyone_finishes(self) -> None:
        a, b = uuid4(), uuid4()
        scores = RoundScorer(self.rules).score([a, b], [a, b])
        assert all(s.gained == 0 for s in scores)

    def test_solo_finisher_gets_bonus(self) -> None:
        a, b = uuid4(), uuid4()
        scores = {s.player_id: s for s in RoundScorer(self.rules).score([a, b], [a])}
        assert scores[a].gained == self.rules.goal + self.rules.solo
        assert scores[b].gained == 0

    def test_first_of_many_gets_first_bonus(self) -> None:
        a, b, c = uuid4(), uuid4(), uuid4()
        scores = {s.player_id: s for s in RoundScorer(self.rules).score([a, b, c], [b, a])}
        assert scores[b].reasons == ["goal", "first"]
        assert scores[a].reasons == ["goal"]
