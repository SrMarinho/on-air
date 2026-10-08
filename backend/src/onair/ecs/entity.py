from typing import NewType

Entity = NewType("Entity", int)


class EntityAllocator:
    """Hands out entity ids, recycling destroyed ones to keep ids small on the wire."""

    def __init__(self) -> None:
        self._next = 1
        self._free: list[Entity] = []

    def allocate(self) -> Entity:
        if self._free:
            return self._free.pop()
        entity = Entity(self._next)
        self._next += 1
        return entity

    def release(self, entity: Entity) -> None:
        self._free.append(entity)
