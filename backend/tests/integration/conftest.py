import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from onair.core.config import Settings
from onair.core.database import Base, Database
from onair.main import create_app
from onair.modules.players.infrastructure import models  # noqa: F401  (registers tables)


async def _create_schema(url: str) -> None:
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    asyncio.run(_create_schema(url))
    settings = Settings(database_url=url, jwt_secret="test-secret-with-at-least-32-bytes!!")
    with TestClient(create_app(settings, Database(url))) as test_client:
        yield test_client


def register(client: TestClient, username: str) -> dict[str, str]:
    response = client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@test.dev", "password": "supersecret"},
    )
    assert response.status_code == 201, response.text
    body: dict[str, str] = response.json()
    return body
