from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from onair.core.config import Settings, get_settings
from onair.core.database import Database
from onair.core.errors import DomainError
from onair.core.security import PasswordHasher, TokenService
from onair.gateway.connection_manager import ConnectionManager
from onair.gateway.dispatcher import Dispatcher
from onair.gateway.endpoint import GameSocketEndpoint
from onair.gateway.handlers import PingHandler
from onair.modules.auth.presentation.router import router as auth_router
from onair.modules.auth.presentation.ws_authenticator import JwtWsAuthenticator
from onair.modules.levels.infrastructure.json_repository import JsonLevelRepository
from onair.modules.levels.presentation.router import router as levels_router
from onair.modules.match.application.match_service import MatchService
from onair.modules.match.application.session_factory import SessionFactory
from onair.modules.match.domain.context import MatchRules
from onair.modules.match.domain.items import default_item_registry
from onair.modules.match.domain.physics import PhysicsConfig
from onair.modules.match.infrastructure.sql_result_recorder import SqlMatchResultRecorder
from onair.modules.match.presentation.ws_handlers import register_match_handlers
from onair.modules.players.presentation.router import router as players_router
from onair.modules.rooms.application.room_service import RoomService
from onair.modules.rooms.infrastructure.memory_repository import InMemoryRoomRepository
from onair.modules.rooms.presentation.router import router as rooms_router
from onair.modules.rooms.presentation.ws_handlers import (
    LeaveRoomOnDisconnect,
    register_room_handlers,
)


def create_app(settings: Settings | None = None, database: Database | None = None) -> FastAPI:
    """Composition root: wires every module's adapters to its ports."""
    settings = settings or get_settings()
    database = database or Database(settings.database_url)
    tokens = TokenService(
        settings.jwt_secret,
        settings.jwt_algorithm,
        settings.access_token_ttl_seconds,
        settings.refresh_token_ttl_seconds,
    )
    connections = ConnectionManager()
    levels = JsonLevelRepository()
    matches = MatchService(
        factory=SessionFactory(levels, default_item_registry, PhysicsConfig(), MatchRules()),
        broadcaster=connections,
        recorder=SqlMatchResultRecorder(database),
        simulation_hz=settings.simulation_hz,
        snapshot_hz=settings.snapshot_hz,
    )
    rooms = RoomService(
        InMemoryRoomRepository(), connections, matches, settings.max_players_per_room
    )
    matches.on_room_finished(rooms.match_finished)

    dispatcher = Dispatcher().register(PingHandler())
    register_room_handlers(dispatcher, rooms)
    register_match_handlers(dispatcher, matches)
    socket = GameSocketEndpoint(
        connections,
        dispatcher,
        JwtWsAuthenticator(tokens, database),
        disconnect_listeners=[LeaveRoomOnDisconnect(rooms)],
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await matches.shutdown()
        await database.dispose()

    app = FastAPI(title="On-Air", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.database = database
    app.state.token_service = tokens
    app.state.password_hasher = PasswordHasher()
    app.state.room_service = rooms
    app.state.level_repository = levels

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code, content={"code": exc.code, "message": exc.message}
        )

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    for router in (auth_router, players_router, rooms_router, levels_router):
        app.include_router(router)
    app.include_router(socket.router("/ws"))
    return app


app = create_app()
