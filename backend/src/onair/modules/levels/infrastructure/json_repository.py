import json
from pathlib import Path

from onair.modules.levels.domain.level import LevelDefinition
from onair.modules.levels.domain.repository import LevelRepository

BUILTIN_LEVELS_DIR = Path(__file__).parent / "data"


class JsonLevelRepository(LevelRepository):
    """Built-in levels shipped as JSON files. Loaded once at startup."""

    def __init__(self, directory: Path = BUILTIN_LEVELS_DIR) -> None:
        self._levels = {level.key: level for level in self._load(directory)}

    def get(self, key: str) -> LevelDefinition | None:
        return self._levels.get(key)

    def all(self) -> list[LevelDefinition]:
        return list(self._levels.values())

    @staticmethod
    def _load(directory: Path) -> list[LevelDefinition]:
        levels = []
        for path in sorted(directory.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            levels.append(
                LevelDefinition(
                    key=path.stem,
                    name=raw["name"],
                    tile_size=raw["tile_size"],
                    rows=tuple(raw["rows"]),
                )
            )
        return levels
