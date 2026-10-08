"""Placeable items. Add a new item by subclassing `ItemDefinition` and registering it."""

import random
from abc import ABC, abstractmethod
from uuid import UUID

from onair.ecs import World
from onair.modules.match.domain.components import (
    Collider,
    Hazard,
    MovingPath,
    PlacedItem,
    Renderable,
    Solid,
    StaticTile,
    Transform,
    Velocity,
)
from onair.modules.match.domain.physics import Rect, rect_of


class ItemDefinition(ABC):
    key: str
    width_tiles: int = 1
    height_tiles: int = 1
    requires_free_space: bool = True

    def footprint(self, tile_x: int, tile_y: int, tile_size: int) -> Rect:
        return Rect(
            tile_x * tile_size,
            tile_y * tile_size,
            self.width_tiles * tile_size,
            self.height_tiles * tile_size,
        )

    @abstractmethod
    def place(self, world: World, area: Rect, owner: UUID, tile_size: int) -> None: ...


class BlockItem(ItemDefinition):
    key = "block"

    def place(self, world: World, area: Rect, owner: UUID, tile_size: int) -> None:
        world.create_entity(
            Transform(area.x, area.y),
            Collider(area.w, area.h),
            Solid(),
            Renderable(self.key),
            PlacedItem(self.key, owner),
        )


class PlankItem(BlockItem):
    key = "plank"
    width_tiles = 3


class SpikesItem(ItemDefinition):
    key = "spikes"
    inset = 6.0

    def place(self, world: World, area: Rect, owner: UUID, tile_size: int) -> None:
        world.create_entity(
            Transform(area.x, area.y + self.inset),
            Collider(area.w, area.h - self.inset),
            Hazard(),
            Renderable(self.key),
            PlacedItem(self.key, owner),
        )


class MovingPlatformItem(ItemDefinition):
    key = "moving_platform"
    width_tiles = 3
    travel_tiles = 4
    speed = 90.0

    def place(self, world: World, area: Rect, owner: UUID, tile_size: int) -> None:
        world.create_entity(
            Transform(area.x, area.y),
            Velocity(),
            Collider(area.w, area.h),
            Solid(),
            MovingPath(
                start_x=area.x,
                start_y=area.y,
                end_x=area.x + self.travel_tiles * tile_size,
                end_y=area.y,
                speed=self.speed,
            ),
            Renderable(self.key),
            PlacedItem(self.key, owner),
        )


class BombItem(ItemDefinition):
    """Destroys placed items (never base-level tiles) in a 3x3 tile area."""

    key = "bomb"
    width_tiles = 3
    height_tiles = 3
    requires_free_space = False

    def place(self, world: World, area: Rect, owner: UUID, tile_size: int) -> None:
        for entity, _ in world.query(PlacedItem):
            if not world.has(entity, StaticTile) and rect_of(world, entity).overlaps(area):
                world.destroy_entity(entity)


class ItemRegistry:
    def __init__(self, items: list[ItemDefinition] | None = None) -> None:
        self._items: dict[str, ItemDefinition] = {}
        for item in items or []:
            self.register(item)

    def register(self, item: ItemDefinition) -> None:
        self._items[item.key] = item

    def get(self, key: str) -> ItemDefinition:
        return self._items[key]

    def keys(self) -> list[str]:
        return list(self._items)

    def draw(self, rng: random.Random, count: int) -> list[str]:
        return [rng.choice(self.keys()) for _ in range(count)]


def default_item_registry() -> ItemRegistry:
    return ItemRegistry([BlockItem(), PlankItem(), SpikesItem(), MovingPlatformItem(), BombItem()])
