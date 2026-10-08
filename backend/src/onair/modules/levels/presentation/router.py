from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from onair.modules.levels.domain.repository import LevelRepository


class LevelSummaryResponse(BaseModel):
    key: str
    name: str
    width: int
    height: int


def level_repository(request: Request) -> LevelRepository:
    repository: LevelRepository = request.app.state.level_repository
    return repository


router = APIRouter(prefix="/levels", tags=["levels"])


@router.get("", response_model=list[LevelSummaryResponse])
async def list_levels(
    levels: Annotated[LevelRepository, Depends(level_repository)],
) -> list[LevelSummaryResponse]:
    return [
        LevelSummaryResponse(key=lv.key, name=lv.name, width=lv.width, height=lv.height)
        for lv in levels.all()
    ]
