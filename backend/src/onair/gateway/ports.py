from typing import Protocol

from onair.gateway.connection import ClientConnection, Identity


class Authenticator(Protocol):
    """Turns the token from the first `auth` frame into an identity or raises."""

    async def authenticate(self, token: str) -> Identity: ...


class DisconnectListener(Protocol):
    async def on_disconnect(self, connection: ClientConnection) -> None: ...
