from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from onair.core.config import Settings
from onair.core.database import Database
from onair.core.security import PasswordHasher, TokenService


def settings(request: Request) -> Settings:
    value: Settings = request.app.state.settings
    return value


async def db_session(request: Request) -> AsyncIterator[AsyncSession]:
    database: Database = request.app.state.database
    async for session in database.session():
        yield session


def token_service(request: Request) -> TokenService:
    value: TokenService = request.app.state.token_service
    return value


def password_hasher(request: Request) -> PasswordHasher:
    value: PasswordHasher = request.app.state.password_hasher
    return value


SettingsDep = Annotated[Settings, Depends(settings)]
SessionDep = Annotated[AsyncSession, Depends(db_session)]
TokenServiceDep = Annotated[TokenService, Depends(token_service)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(password_hasher)]
