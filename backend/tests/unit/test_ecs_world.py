from dataclasses import dataclass

import pytest

from onair.ecs import Component, Scheduler, System, World


@dataclass(slots=True)
class Position(Component):
    x: float


@dataclass(slots=True)
class Speed(Component):
    value: float


class MoveSystem(System):
    def update(self, world: World, dt: float) -> None:
        for _, pos, speed in world.query(Position, Speed):
            pos.x += speed.value * dt


def test_query_returns_only_entities_with_all_components() -> None:
    world = World()
    moving = world.create_entity(Position(0), Speed(1))
    world.create_entity(Position(5))

    assert [entity for entity, *_ in world.query(Position, Speed)] == [moving]


def test_scheduler_runs_systems_and_applies_deferred_destroy() -> None:
    world = World()
    entity = world.create_entity(Position(0), Speed(10))
    scheduler = Scheduler([MoveSystem()])

    scheduler.tick(world, 0.5)
    assert world.require(entity, Position).x == 5

    world.destroy_entity(entity)
    assert not world.is_alive(entity)
    assert list(world.query(Position)) == []
    scheduler.tick(world, 0.5)
    assert entity not in world.entities


def test_destroyed_ids_are_recycled() -> None:
    world = World()
    first = world.create_entity()
    world.destroy_entity(first)
    world.flush()

    assert world.create_entity() == first


def test_add_component_to_missing_entity_fails() -> None:
    with pytest.raises(KeyError):
        World().add_component(999, Position(0))  # type: ignore[arg-type]


def test_events_are_read_by_type_and_cleared() -> None:
    world = World()
    world.events.emit("hello")
    world.events.emit(42)

    assert world.events.read(str) == ["hello"]
    world.events.clear()
    assert world.events.read(int) == []
