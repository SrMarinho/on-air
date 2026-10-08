from dataclasses import dataclass
from enum import StrEnum


class Tile(StrEnum):
    EMPTY = "."
    SOLID = "#"
    SPIKES = "^"
    SPAWN = "S"
    GOAL = "G"


class InvalidLevelError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class LevelDefinition:
    """Tile grid, row 0 at the top. Pure data; the match module turns it into entities."""

    key: str
    name: str
    tile_size: int
    rows: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise InvalidLevelError("Level has no rows")
        if len({len(row) for row in self.rows}) != 1:
            raise InvalidLevelError("Every row must have the same width")
        valid = {t.value for t in Tile}
        if any(ch not in valid for row in self.rows for ch in row):
            raise InvalidLevelError("Unknown tile character")
        if not self.positions_of(Tile.SPAWN):
            raise InvalidLevelError("Level needs at least one spawn")
        if len(self.positions_of(Tile.GOAL)) != 1:
            raise InvalidLevelError("Level needs exactly one goal")

    @property
    def width(self) -> int:
        return len(self.rows[0])

    @property
    def height(self) -> int:
        return len(self.rows)

    def tile_at(self, x: int, y: int) -> Tile:
        return Tile(self.rows[y][x])

    def positions_of(self, tile: Tile) -> list[tuple[int, int]]:
        return [
            (x, y)
            for y, row in enumerate(self.rows)
            for x, ch in enumerate(row)
            if ch == tile.value
        ]

    def horizontal_runs(self, tile: Tile) -> list[tuple[int, int, int]]:
        """Merge consecutive tiles per row into `(x, y, length)` so physics checks fewer boxes."""
        runs: list[tuple[int, int, int]] = []
        for y, row in enumerate(self.rows):
            start: int | None = None
            for x, ch in enumerate([*row, Tile.EMPTY.value]):
                if ch == tile.value and start is None:
                    start = x
                elif ch != tile.value and start is not None:
                    runs.append((start, y, x - start))
                    start = None
        return runs
