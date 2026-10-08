from collections.abc import Iterable

from onair.ecs.system import System
from onair.ecs.world import World


class Scheduler:
    """Runs systems in declared order, then applies deferred entity destruction."""

    def __init__(self, systems: Iterable[System] = ()) -> None:
        self._systems: list[System] = list(systems)

    def add(self, system: System) -> "Scheduler":
        self._systems.append(system)
        return self

    def tick(self, world: World, dt: float) -> None:
        for system in self._systems:
            system.update(world, dt)
        world.flush()
