"""Pure-data components for the platformer simulation. Positions are top-left, in pixels."""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from onair.ecs import Component, Entity


@dataclass(slots=True)
class Transform(Component):
    x: float
    y: float


@dataclass(slots=True)
class Velocity(Component):
    vx: float = 0.0
    vy: float = 0.0


@dataclass(slots=True)
class Collider(Component):
    w: float
    h: float


@dataclass(slots=True)
class Body(Component):
    """Dynamic body moved and resolved by the physics system."""

    gravity_scale: float = 1.0


@dataclass(slots=True)
class Contacts(Component):
    on_ground: bool = False
    wall_left: bool = False
    wall_right: bool = False
    ground: Entity | None = None
    coyote_time_left: float = 0.0


@dataclass(slots=True)
class PlayerInput(Component):
    left: bool = False
    right: bool = False
    jump: bool = False
    previous_jump: bool = False
    jump_buffer_left: float = 0.0
    last_seq: int = 0


class LifeState(StrEnum):
    ALIVE = "alive"
    DEAD = "dead"
    FINISHED = "finished"


@dataclass(slots=True)
class PlayerTag(Component):
    player_id: UUID
    state: LifeState = LifeState.ALIVE

    @property
    def alive(self) -> bool:
        return self.state is LifeState.ALIVE


@dataclass(slots=True)
class Solid(Component):
    pass


@dataclass(slots=True)
class Hazard(Component):
    pass


@dataclass(slots=True)
class Goal(Component):
    pass


@dataclass(slots=True)
class StaticTile(Component):
    """Part of the base level; never sent in snapshots nor destroyed by bombs."""


@dataclass(slots=True)
class Renderable(Component):
    kind: str


@dataclass(slots=True)
class PlacedItem(Component):
    item_key: str
    owner: UUID


@dataclass(slots=True)
class MovingPath(Component):
    """Ping-pong kinematic motion between two points at constant speed."""

    start_x: float
    start_y: float
    end_x: float
    end_y: float
    speed: float
    progress: float = 0.0
    forward: bool = True
