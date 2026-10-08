from typing import Protocol
from uuid import UUID


class MatchResultRecorder(Protocol):
    async def record(self, participants: list[UUID], winner_id: UUID | None) -> None: ...
