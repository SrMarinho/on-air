from collections import defaultdict
from typing import TypeVar

E = TypeVar("E")


class EventBus:
    """Per-tick event queue: systems emit, later systems/phases read, then it is cleared."""

    def __init__(self) -> None:
        self._events: defaultdict[type[object], list[object]] = defaultdict(list)

    def emit(self, event: object) -> None:
        self._events[type(event)].append(event)

    def read(self, event_type: type[E]) -> list[E]:
        return list(self._events.get(event_type, []))  # type: ignore[arg-type]

    def clear(self) -> None:
        self._events.clear()
