from dataclasses import dataclass

from onair.ecs import World
from onair.modules.levels.domain.level import LevelDefinition, Tile
from onair.modules.match.domain.components import (
    Collider,
    Goal,
    Hazard,
    Renderable,
    Solid,
    StaticTile,
    Transform,
)
from onair.modules.match.domain.physics import Rect

SPIKE_INSET = 6.0
KEEP_OUT_MARGIN_TILES = 1


@dataclass(frozen=True, slots=True)
class LevelRuntime:
    definition: LevelDefinition
    spawns: tuple[tuple[float, float], ...]
    keep_out: tuple[Rect, ...]

    @property
    def bounds(self) -> Rect:
        size = self.definition.tile_size
        return Rect(0, 0, self.definition.width * size, self.definition.height * size)


class LevelBuilder:
    """Turns a tile grid into static ECS entities and spawn/keep-out data."""

    def build(self, world: World, level: LevelDefinition) -> LevelRuntime:
        size = level.tile_size
        for x, y, length in level.horizontal_runs(Tile.SOLID):
            world.create_entity(
                Transform(x * size, y * size),
                Collider(length * size, size),
                Solid(),
                StaticTile(),
                Renderable("ground"),
            )
        for x, y, length in level.horizontal_runs(Tile.SPIKES):
            world.create_entity(
                Transform(x * size, y * size + SPIKE_INSET),
                Collider(length * size, size - SPIKE_INSET),
                Hazard(),
                StaticTile(),
                Renderable("spikes"),
            )
        goal_x, goal_y = level.positions_of(Tile.GOAL)[0]
        world.create_entity(
            Transform(goal_x * size, goal_y * size),
            Collider(size, size),
            Goal(),
            StaticTile(),
            Renderable("goal"),
        )
        spawn_tiles = level.positions_of(Tile.SPAWN)
        return LevelRuntime(
            definition=level,
            spawns=tuple((x * size, y * size) for x, y in spawn_tiles),
            keep_out=tuple(self._keep_out(x, y, size) for x, y in [*spawn_tiles, (goal_x, goal_y)]),
        )

    @staticmethod
    def _keep_out(tile_x: int, tile_y: int, size: int) -> Rect:
        margin = KEEP_OUT_MARGIN_TILES * size
        return Rect(
            tile_x * size - margin, tile_y * size - margin, size + 2 * margin, size + 2 * margin
        )
