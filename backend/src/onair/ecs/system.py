from abc import ABC, abstractmethod

from onair.ecs.world import World


class System(ABC):
    """Behaviour over components. Keep one responsibility per system."""

    @abstractmethod
    def update(self, world: World, dt: float) -> None: ...
