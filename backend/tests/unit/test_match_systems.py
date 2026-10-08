from uuid import uuid4

from onair.ecs import Entity, World
from onair.modules.match.domain.components import (
    Body,
    Collider,
    Contacts,
    Goal,
    Hazard,
    LifeState,
    MovingPath,
    PlayerInput,
    PlayerTag,
    Solid,
    Transform,
    Velocity,
)
from onair.modules.match.domain.events import PlayerDied, PlayerReachedGoal
from onair.modules.match.domain.physics import PhysicsConfig
from onair.modules.match.domain.systems import build_scheduler

CONFIG = PhysicsConfig()
DT = 1 / 60


def _world_with_floor() -> World:
    world = World()
    world.create_entity(Transform(0, 300), Collider(1000, 32), Solid())
    return world


def _player(world: World, x: float = 100, y: float = 200) -> Entity:
    return world.create_entity(
        Transform(x, y),
        Velocity(),
        Collider(CONFIG.player_width, CONFIG.player_height),
        Body(),
        Contacts(),
        PlayerInput(),
        PlayerTag(uuid4()),
    )


def _run(world: World, ticks: int) -> None:
    scheduler = build_scheduler(CONFIG, level_height_px=1000)
    for _ in range(ticks):
        scheduler.tick(world, DT)


def test_player_falls_and_lands_on_floor() -> None:
    world = _world_with_floor()
    player = _player(world)

    _run(world, 60)

    assert world.require(player, Transform).y == 300 - CONFIG.player_height
    assert world.require(player, Contacts).on_ground


def test_jump_lifts_player_off_ground() -> None:
    world = _world_with_floor()
    player = _player(world)
    _run(world, 60)
    world.require(player, PlayerInput).jump = True

    _run(world, 10)

    assert world.require(player, Transform).y < 300 - CONFIG.player_height - 50
    assert not world.require(player, Contacts).on_ground


def test_running_right_moves_player_right() -> None:
    world = _world_with_floor()
    player = _player(world)
    world.require(player, PlayerInput).right = True

    _run(world, 60)

    assert world.require(player, Transform).x > 300


def test_wall_stops_horizontal_motion() -> None:
    world = _world_with_floor()
    world.create_entity(Transform(200, 0), Collider(32, 300), Solid())
    player = _player(world)
    world.require(player, PlayerInput).right = True

    _run(world, 60)

    assert world.require(player, Transform).x == 200 - CONFIG.player_width
    assert world.require(player, Contacts).wall_right


def test_hazard_kills_player_and_emits_event() -> None:
    world = _world_with_floor()
    world.create_entity(Transform(90, 280), Collider(64, 20), Hazard())
    player = _player(world)
    seen: list[PlayerDied] = []

    scheduler = build_scheduler(CONFIG, level_height_px=1000)
    for _ in range(60):
        scheduler.tick(world, DT)
        seen += world.events.read(PlayerDied)
        world.events.clear()

    assert world.require(player, PlayerTag).state is LifeState.DEAD
    assert len(seen) == 1


def test_goal_finishes_player() -> None:
    world = _world_with_floor()
    world.create_entity(Transform(100, 260), Collider(32, 32), Goal())
    player = _player(world)

    _run(world, 30)

    assert world.require(player, PlayerTag).state is LifeState.FINISHED
    assert world.events.read(PlayerReachedGoal)


def test_falling_out_of_level_kills_player() -> None:
    world = World()
    player = _player(world)

    _run(world, 120)

    assert world.require(player, PlayerTag).state is LifeState.DEAD


def test_moving_platform_carries_rider() -> None:
    world = World()
    world.create_entity(
        Transform(0, 300),
        Velocity(),
        Collider(96, 16),
        Solid(),
        MovingPath(start_x=0, start_y=300, end_x=400, end_y=300, speed=100),
    )
    player = _player(world, x=30, y=260)
    _run(world, 30)
    start_x = world.require(player, Transform).x

    _run(world, 60)

    assert world.require(player, Transform).x > start_x + 80
    assert world.require(player, Contacts).on_ground
