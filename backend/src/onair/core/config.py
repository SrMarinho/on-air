from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ONAIR_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://onair:onair@localhost:5432/onair"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 15 * 60
    refresh_token_ttl_seconds: int = 7 * 24 * 60 * 60
    cors_origins: list[str] = ["http://localhost:5173"]

    simulation_hz: int = 60
    snapshot_hz: int = 30
    max_players_per_room: int = 4

    pick_seconds: float = 15.0
    place_seconds: float = 20.0
    run_seconds: float = 60.0
    score_seconds: float = 4.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
