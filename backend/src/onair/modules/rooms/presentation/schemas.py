from uuid import UUID

from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    name: str = Field(min_length=1, max_length=40)


class RoomSummaryResponse(BaseModel):
    id: UUID
    name: str
    players: int
    max_players: int
