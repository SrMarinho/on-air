from fastapi import APIRouter

from onair.modules.auth.presentation.dependencies import CurrentPlayerIdDep
from onair.modules.players.application.get_profile import GetProfile
from onair.modules.players.presentation.dependencies import PlayerRepositoryDep
from onair.modules.players.presentation.schemas import PlayerProfileResponse

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/me", response_model=PlayerProfileResponse)
async def me(player_id: CurrentPlayerIdDep, players: PlayerRepositoryDep) -> PlayerProfileResponse:
    player = await GetProfile(players).execute(player_id)
    return PlayerProfileResponse(
        id=player.id,
        username=player.username,
        matches_played=player.matches_played,
        matches_won=player.matches_won,
        created_at=player.created_at,
    )
