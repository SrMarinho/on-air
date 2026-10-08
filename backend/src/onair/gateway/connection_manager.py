from collections import defaultdict
from uuid import UUID

from onair.core.ports import Broadcaster
from onair.gateway.connection import ClientConnection
from onair.protocol.base import Message


class ConnectionManager(Broadcaster):
    """Tracks live connections and which room each one listens to."""

    def __init__(self) -> None:
        self._connections: dict[UUID, ClientConnection] = {}
        self._room_of: dict[UUID, UUID] = {}
        self._room_members: defaultdict[UUID, set[UUID]] = defaultdict(set)

    def register(self, connection: ClientConnection) -> ClientConnection | None:
        """Register and return a previous connection of the same player, if any."""
        previous = self._connections.get(connection.player_id)
        self._connections[connection.player_id] = connection
        return previous

    def unregister(self, connection: ClientConnection) -> bool:
        """Remove only if it is still the active connection for that player."""
        if self._connections.get(connection.player_id) is not connection:
            return False
        del self._connections[connection.player_id]
        return True

    def bind_room(self, player_id: UUID, room_id: UUID | None) -> None:
        old = self._room_of.pop(player_id, None)
        if old is not None:
            self._room_members[old].discard(player_id)
            if not self._room_members[old]:
                del self._room_members[old]
        if room_id is not None:
            self._room_of[player_id] = room_id
            self._room_members[room_id].add(player_id)

    async def send_to_player(self, player_id: UUID, message: Message) -> None:
        connection = self._connections.get(player_id)
        if connection is not None:
            connection.send(message)

    async def send_to_room(self, room_id: UUID, message: Message) -> None:
        for player_id in tuple(self._room_members.get(room_id, ())):
            await self.send_to_player(player_id, message)
