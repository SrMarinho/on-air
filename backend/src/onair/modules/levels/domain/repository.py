from abc import ABC, abstractmethod

from onair.modules.levels.domain.level import LevelDefinition


class LevelRepository(ABC):
    @abstractmethod
    def get(self, key: str) -> LevelDefinition | None: ...

    @abstractmethod
    def all(self) -> list[LevelDefinition]: ...
