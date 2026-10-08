from dataclasses import dataclass

from onair.ecs import Entity, World
from onair.modules.match.domain.components import Collider, Transform


@dataclass(frozen=True, slots=True)
class PhysicsConfig:
    """Platformer tuning, px and seconds. Clients mirror these for local prediction."""

    gravity: float = 2200.0
    max_fall_speed: float = 900.0
    run_speed: float = 260.0
    ground_accel: float = 3000.0
    air_accel: float = 1800.0
    jump_speed: float = 720.0
    jump_release_speed: float = 300.0
    coyote_time: float = 0.1
    jump_buffer_time: float = 0.12
    wall_slide_speed: float = 180.0
    wall_jump_push: float = 320.0
    player_width: float = 24.0
    player_height: float = 30.0


@dataclass(frozen=True, slots=True)
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def overlaps(self, other: "Rect") -> bool:
        return (
            self.x < other.right
            and other.x < self.right
            and self.y < other.bottom
            and other.y < self.bottom
        )


def rect_of(world: World, entity: Entity) -> Rect:
    transform = world.require(entity, Transform)
    collider = world.require(entity, Collider)
    return Rect(transform.x, transform.y, collider.w, collider.h)
