from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from onair.core.dependencies import TokenServiceDep
from onair.core.errors import UnauthorizedError
from onair.modules.auth.application.use_cases import TokenPairIssuer

_bearer = HTTPBearer(auto_error=False)


def current_player_id(
    tokens: TokenServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> UUID:
    if credentials is None:
        raise UnauthorizedError("Missing bearer token")
    return tokens.verify(credentials.credentials, "access")


def token_pair_issuer(tokens: TokenServiceDep) -> TokenPairIssuer:
    return TokenPairIssuer(tokens)


CurrentPlayerIdDep = Annotated[UUID, Depends(current_player_id)]
TokenPairIssuerDep = Annotated[TokenPairIssuer, Depends(token_pair_issuer)]
