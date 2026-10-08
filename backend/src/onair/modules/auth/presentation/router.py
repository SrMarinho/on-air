from fastapi import APIRouter, status

from onair.core.dependencies import PasswordHasherDep, TokenServiceDep
from onair.modules.auth.application.dto import TokenPair
from onair.modules.auth.application.use_cases import Login, RefreshTokens, RegisterPlayer
from onair.modules.auth.presentation.dependencies import TokenPairIssuerDep
from onair.modules.auth.presentation.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from onair.modules.players.presentation.dependencies import PlayerRepositoryDep

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_response(pair: TokenPair) -> TokenResponse:
    return TokenResponse(
        player_id=pair.player_id,
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    players: PlayerRepositoryDep,
    hasher: PasswordHasherDep,
    issuer: TokenPairIssuerDep,
) -> TokenResponse:
    pair = await RegisterPlayer(players, hasher, issuer).execute(
        username=body.username, email=body.email, password=body.password
    )
    return _to_response(pair)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    players: PlayerRepositoryDep,
    hasher: PasswordHasherDep,
    issuer: TokenPairIssuerDep,
) -> TokenResponse:
    pair = await Login(players, hasher, issuer).execute(
        username=body.username, password=body.password
    )
    return _to_response(pair)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    players: PlayerRepositoryDep,
    tokens: TokenServiceDep,
    issuer: TokenPairIssuerDep,
) -> TokenResponse:
    return _to_response(await RefreshTokens(players, tokens, issuer).execute(body.refresh_token))
