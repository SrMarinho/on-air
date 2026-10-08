from collections.abc import Iterator
from typing import TypeVar, overload

from onair.ecs.component import Component
from onair.ecs.entity import Entity, EntityAllocator
from onair.ecs.events import EventBus

C = TypeVar("C", bound=Component)
C1 = TypeVar("C1", bound=Component)
C2 = TypeVar("C2", bound=Component)
C3 = TypeVar("C3", bound=Component)
C4 = TypeVar("C4", bound=Component)


class World:
    """Owns entities and their components. Holds no game rules."""

    def __init__(self) -> None:
        self._allocator = EntityAllocator()
        self._entities: set[Entity] = set()
        self._stores: dict[type[Component], dict[Entity, Component]] = {}
        self._pending_destroy: set[Entity] = set()
        self.events = EventBus()

    # --- entities -------------------------------------------------------
    def create_entity(self, *components: Component) -> Entity:
        entity = self._allocator.allocate()
        self._entities.add(entity)
        for component in components:
            self.add_component(entity, component)
        return entity

    def destroy_entity(self, entity: Entity) -> None:
        """Deferred: applied in `flush()` so systems can iterate safely."""
        if entity in self._entities:
            self._pending_destroy.add(entity)

    def flush(self) -> None:
        for entity in self._pending_destroy:
            for store in self._stores.values():
                store.pop(entity, None)
            self._entities.discard(entity)
            self._allocator.release(entity)
        self._pending_destroy.clear()

    def is_alive(self, entity: Entity) -> bool:
        return entity in self._entities and entity not in self._pending_destroy

    @property
    def entities(self) -> frozenset[Entity]:
        return frozenset(self._entities)

    # --- components -----------------------------------------------------
    def add_component(self, entity: Entity, component: Component) -> None:
        if entity not in self._entities:
            raise KeyError(f"Entity {entity} does not exist")
        self._stores.setdefault(type(component), {})[entity] = component

    def remove_component(self, entity: Entity, component_type: type[Component]) -> None:
        self._stores.get(component_type, {}).pop(entity, None)

    def get(self, entity: Entity, component_type: type[C]) -> C | None:
        return self._stores.get(component_type, {}).get(entity)  # type: ignore[return-value]

    def require(self, entity: Entity, component_type: type[C]) -> C:
        component = self.get(entity, component_type)
        if component is None:
            raise KeyError(f"Entity {entity} has no {component_type.__name__}")
        return component

    def has(self, entity: Entity, *component_types: type[Component]) -> bool:
        return all(entity in self._stores.get(t, {}) for t in component_types)

    # --- queries --------------------------------------------------------
    @overload
    def query(self, t1: type[C1], /) -> Iterator[tuple[Entity, C1]]: ...
    @overload
    def query(self, t1: type[C1], t2: type[C2], /) -> Iterator[tuple[Entity, C1, C2]]: ...
    @overload
    def query(
        self, t1: type[C1], t2: type[C2], t3: type[C3], /
    ) -> Iterator[tuple[Entity, C1, C2, C3]]: ...
    @overload
    def query(
        self, t1: type[C1], t2: type[C2], t3: type[C3], t4: type[C4], /
    ) -> Iterator[tuple[Entity, C1, C2, C3, C4]]: ...
    def query(self, *types: type[Component]) -> Iterator[tuple[object, ...]]:
        """Yield `(entity, *components)` for live entities owning every given type.

        Iterates the smallest store first; result is materialized so callers may mutate
        the world (add/remove components) while looping.
        """
        stores = [self._stores.get(t, {}) for t in types]
        smallest = min(stores, key=len)
        matches = [
            (entity, *(store[entity] for store in stores))
            for entity in sorted(smallest)
            if entity not in self._pending_destroy and all(entity in s for s in stores)
        ]
        yield from matches
