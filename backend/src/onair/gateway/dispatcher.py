from abc import ABC, abstractmethod
from typing import Any

from onair.gateway.connection import ClientConnection
from onair.protocol.base import Message


class MessageHandler[M: Message](ABC):
    """Handles one client message type. Register new handlers instead of editing the
    dispatcher (open/closed)."""

    message_type: type[M]

    @abstractmethod
    async def handle(self, connection: ClientConnection, message: M) -> None: ...


class UnknownMessageError(Exception):
    pass


class Dispatcher:
    def __init__(self) -> None:
        self._handlers: dict[type[Message], MessageHandler[Any]] = {}

    def register(self, handler: MessageHandler[Any]) -> "Dispatcher":
        if handler.message_type in self._handlers:
            raise ValueError(f"Handler already registered for {handler.message_type.__name__}")
        self._handlers[handler.message_type] = handler
        return self

    async def dispatch(self, connection: ClientConnection, message: Message) -> None:
        handler = self._handlers.get(type(message))
        if handler is None:
            raise UnknownMessageError(type(message).__name__)
        await handler.handle(connection, message)
