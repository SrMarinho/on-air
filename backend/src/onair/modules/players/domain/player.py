from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class Player:
    username: str
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    matches_played: int = 0
    matches_won: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def record_match(self, *, won: bool) -> None:
        self.matches_played += 1
        if won:
            self.matches_won += 1
