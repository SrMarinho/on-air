"""Simulation systems, in the order they run each tick (see `build_scheduler`)."""

from onair.ecs import Entity, Scheduler, System, World
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
from onair.modules.match.domain.physics import PhysicsConfig, Rect, rect_of


def _approach(current: float, target: float, max_delta: float) -> float:
    if current < target:
        return min(current + max_delta, target)
    return max(current - max_delta, target)


def _end_life(world: World, entity: Entity, tag: PlayerTag, state: LifeState) -> None:
    tag.state = state
    world.remove_component(entity, Body)
    velocity = world.get(entity, Velocity)
    if velocity is not None:
        velocity.vx = velocity.vy = 0.0


class KinematicPathSystem(System):
    """Moves path-following solids and exposes their velocity so riders get carried."""

    def update(self, world: World, dt: float) -> None:
        for _, path, transform, velocity in world.query(MovingPath, Transform, Velocity):
            dx, dy = path.end_x - path.start_x, path.end_y - path.start_y
            length = max((dx * dx + dy * dy) ** 0.5, 1e-6)
            step = path.speed * dt / length
            path.progress += step if path.forward else -step
            if path.progress >= 1.0:
                path.progress, path.forward = 1.0, False
            elif path.progress <= 0.0:
                path.progress, path.forward = 0.0, True
            new_x = path.start_x + dx * path.progress
            new_y = path.start_y + dy * path.progress
            velocity.vx = (new_x - transform.x) / dt
            velocity.vy = (new_y - transform.y) / dt
            transform.x, transform.y = new_x, new_y


class GravitySystem(System):
    def __init__(self, config: PhysicsConfig) -> None:
        self._config = config

    def update(self, world: World, dt: float) -> None:
        for _, body, velocity in world.query(Body, Velocity):
            velocity.vy = min(
                velocity.vy + self._config.gravity * body.gravity_scale * dt,
                self._config.max_fall_speed,
            )


class PlayerControlSystem(System):
    """Input → velocity: run, buffered/coyote jump, variable jump height, wall slide/jump."""

    def __init__(self, config: PhysicsConfig) -> None:
        self._config = config

    def update(self, world: World, dt: float) -> None:
        cfg = self._config
        for _, tag, inp, velocity, contacts in world.query(
            PlayerTag, PlayerInput, Velocity, Contacts
        ):
            if not tag.alive:
                continue
            direction = int(inp.right) - int(inp.left)
            accel = cfg.ground_accel if contacts.on_ground else cfg.air_accel
            velocity.vx = _approach(velocity.vx, direction * cfg.run_speed, accel * dt)

            if inp.jump and not inp.previous_jump:
                inp.jump_buffer_left = cfg.jump_buffer_time
            else:
                inp.jump_buffer_left = max(0.0, inp.jump_buffer_left - dt)
            inp.previous_jump = inp.jump

            touching_wall = contacts.wall_left or contacts.wall_right
            if inp.jump_buffer_left > 0.0:
                if contacts.on_ground or contacts.coyote_time_left > 0.0:
                    velocity.vy = -cfg.jump_speed
                    inp.jump_buffer_left = contacts.coyote_time_left = 0.0
                elif touching_wall:
                    away = 1 if contacts.wall_left else -1
                    velocity.vy = -cfg.jump_speed
                    velocity.vx = away * cfg.wall_jump_push
                    inp.jump_buffer_left = 0.0

            if not inp.jump and velocity.vy < -cfg.jump_release_speed:
                velocity.vy = -cfg.jump_release_speed

            pressing_wall = (contacts.wall_left and direction < 0) or (
                contacts.wall_right and direction > 0
            )
            if pressing_wall and not contacts.on_ground and velocity.vy > cfg.wall_slide_speed:
                velocity.vy = cfg.wall_slide_speed


class PhysicsSystem(System):
    """Axis-separated AABB movement against `Solid` boxes; updates `Contacts`."""

    def __init__(self, config: PhysicsConfig) -> None:
        self._config = config

    def update(self, world: World, dt: float) -> None:
        solids = [(entity, rect_of(world, entity)) for entity, _ in world.query(Solid)]
        for entity, _, transform, velocity, collider in world.query(
            Body, Transform, Velocity, Collider
        ):
            contacts = world.get(entity, Contacts) or Contacts()
            carry_x, carry_y = self._carry(world, contacts, dt)

            transform.x += velocity.vx * dt + carry_x
            contacts.wall_left = contacts.wall_right = False
            for _, solid in solids:
                box = Rect(transform.x, transform.y, collider.w, collider.h)
                if not box.overlaps(solid):
                    continue
                if velocity.vx > 0 or carry_x > 0:
                    transform.x = solid.x - collider.w
                    contacts.wall_right = True
                else:
                    transform.x = solid.right
                    contacts.wall_left = True
                velocity.vx = 0.0

            transform.y += velocity.vy * dt + carry_y
            contacts.on_ground, contacts.ground = False, None
            for solid_entity, solid in solids:
                box = Rect(transform.x, transform.y, collider.w, collider.h)
                if not box.overlaps(solid):
                    continue
                if velocity.vy >= 0:
                    transform.y = solid.y - collider.h
                    contacts.on_ground, contacts.ground = True, solid_entity
                else:
                    transform.y = solid.bottom
                velocity.vy = 0.0

            if contacts.on_ground:
                contacts.coyote_time_left = self._config.coyote_time
            else:
                contacts.coyote_time_left = max(0.0, contacts.coyote_time_left - dt)

    @staticmethod
    def _carry(world: World, contacts: Contacts, dt: float) -> tuple[float, float]:
        if contacts.ground is None or not world.is_alive(contacts.ground):
            return 0.0, 0.0
        ground_velocity = world.get(contacts.ground, Velocity)
        if ground_velocity is None:
            return 0.0, 0.0
        return ground_velocity.vx * dt, ground_velocity.vy * dt


class HazardSystem(System):
    def update(self, world: World, dt: float) -> None:
        hazards = [rect_of(world, entity) for entity, _ in world.query(Hazard)]
        for entity, tag in world.query(PlayerTag):
            if tag.alive and any(rect_of(world, entity).overlaps(h) for h in hazards):
                _end_life(world, entity, tag, LifeState.DEAD)
                world.events.emit(PlayerDied(tag.player_id))


class GoalSystem(System):
    def update(self, world: World, dt: float) -> None:
        goals = [rect_of(world, entity) for entity, _ in world.query(Goal)]
        for entity, tag in world.query(PlayerTag):
            if tag.alive and any(rect_of(world, entity).overlaps(g) for g in goals):
                _end_life(world, entity, tag, LifeState.FINISHED)
                world.events.emit(PlayerReachedGoal(tag.player_id))


class OutOfBoundsSystem(System):
    def __init__(self, kill_y: float) -> None:
        self._kill_y = kill_y

    def update(self, world: World, dt: float) -> None:
        for entity, tag, transform in world.query(PlayerTag, Transform):
            if tag.alive and transform.y > self._kill_y:
                _end_life(world, entity, tag, LifeState.DEAD)
                world.events.emit(PlayerDied(tag.player_id))


def build_scheduler(config: PhysicsConfig, level_height_px: float) -> Scheduler:
    return Scheduler(
        [
            KinematicPathSystem(),
            GravitySystem(config),
            PlayerControlSystem(config),
            PhysicsSystem(config),
            HazardSystem(),
            GoalSystem(),
            OutOfBoundsSystem(kill_y=level_height_px + 64),
        ]
    )
