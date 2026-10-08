from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from onair.modules.auth.presentation.dependencies import CurrentPlayerIdDep
from onair.modules.rooms.application.room_service import RoomService
from onair.modules.rooms.domain.room import Room
from onair.modules.rooms.presentation.schemas import CreateRoomRequest, RoomSummaryResponse


def room_service(request: Request) -> RoomService:
    service: RoomService = request.app.state.room_service
    return service


RoomServiceDep = Annotated[RoomService, Depends(room_service)]

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _summary(room: Room) -> RoomSummaryResponse:
    return RoomSummaryResponse(
        id=room.id, name=room.name, players=len(room.members), max_players=room.max_players
    )


@router.get("", response_model=list[RoomSummaryResponse])
async def list_rooms(_: CurrentPlayerIdDep, rooms: RoomServiceDep) -> list[RoomSummaryResponse]:
    return [_summary(room) for room in rooms.list_open()]


@router.post("", response_model=RoomSummaryResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    body: CreateRoomRequest, _: CurrentPlayerIdDep, rooms: RoomServiceDep
) -> RoomSummaryResponse:
    return _summary(rooms.create(body.name))
