from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PlayerProfileResponse(BaseModel):
    id: UUID
    username: str
    matches_played: int
    matches_won: int
    created_at: datetime
