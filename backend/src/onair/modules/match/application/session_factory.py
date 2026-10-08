import random
from collections.abc import Callable, Sequence
from uuid import UUID

from onair.core.errors import NotFoundError
from onair.ecs import World
from onair.modules.levels.domain.repository import LevelRepository
from onair.modules.match.domain.context import MatchContext, MatchRules, Participant
from onair.modules.match.domain.items import ItemRegistry
from onair.modules.match.domain.level_builder import LevelBuilder
from onair.modules.match.domain.physics import PhysicsConfig
from onair.modules.match.domain.session import GameSession
from onair.modules.match.domain.systems import build_scheduler

PLAYER_COLORS = (0xF5C518, 0x3FA7F5, 0xF55D3E, 0x6BCB77, 0xB07CF5, 0xF58AC8)


class SessionFactory:
    def __init__(
        self,
        levels: LevelRepository,
        item_registry: Callable[[], ItemRegistry],
        physics: PhysicsConfig,
        rules: MatchRules,
        level_key: str = "meadow",
        seed: int | None = None,
    ) -> None:
        self._levels = levels
        self._item_registry = item_registry
        self._physics = physics
        self._rules = rules
        self._level_key = level_key
        self._seed = seed

    def create(self, players: Sequence[tuple[UUID, str]]) -> GameSession:
        level = self._levels.get(self._level_key)
        if level is None:
            raise NotFoundError(f"Level '{self._level_key}' not found")
        world = World()
        runtime = LevelBuilder().build(world, level)
        participants = {
            player_id: Participant(player_id, username, PLAYER_COLORS[i % len(PLAYER_COLORS)])
            for i, (player_id, username) in enumerate(players)
        }
        ctx = MatchContext(
            world=world,
            scheduler=build_scheduler(self._physics, runtime.bounds.bottom),
            level=runtime,
            items=self._item_registry(),
            physics=self._physics,
            rules=self._rules,
            rng=random.Random(self._seed),
            participants=participants,
        )
        return GameSession(ctx)
