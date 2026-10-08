import time

from onair.gateway.connection import ClientConnection
from onair.gateway.dispatcher import MessageHandler
from onair.protocol.client import PingMessage
from onair.protocol.server import PongMessage


class PingHandler(MessageHandler[PingMessage]):
    message_type = PingMessage

    async def handle(self, connection: ClientConnection, message: PingMessage) -> None:
        connection.send(PongMessage(client_time=message.client_time, server_time=time.time()))
