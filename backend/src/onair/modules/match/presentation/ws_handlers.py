from onair.gateway.connection import ClientConnection
from onair.gateway.dispatcher import Dispatcher, MessageHandler
from onair.modules.match.application.match_service import MatchService
from onair.protocol.client import InputMessage, PickItemMessage, PlaceItemMessage


class InputHandler(MessageHandler[InputMessage]):
    message_type = InputMessage

    def __init__(self, matches: MatchService) -> None:
        self._matches = matches

    async def handle(self, connection: ClientConnection, message: InputMessage) -> None:
        self._matches.session_for(connection.player_id).apply_input(
            connection.player_id, message.seq, message.left, message.right, message.jump
        )


class PickItemHandler(MessageHandler[PickItemMessage]):
    message_type = PickItemMessage

    def __init__(self, matches: MatchService) -> None:
        self._matches = matches

    async def handle(self, connection: ClientConnection, message: PickItemMessage) -> None:
        self._matches.session_for(connection.player_id).pick(connection.player_id, message.offer_id)


class PlaceItemHandler(MessageHandler[PlaceItemMessage]):
    message_type = PlaceItemMessage

    def __init__(self, matches: MatchService) -> None:
        self._matches = matches

    async def handle(self, connection: ClientConnection, message: PlaceItemMessage) -> None:
        self._matches.session_for(connection.player_id).place(
            connection.player_id, message.tile_x, message.tile_y
        )


def register_match_handlers(dispatcher: Dispatcher, matches: MatchService) -> None:
    dispatcher.register(InputHandler(matches))
    dispatcher.register(PickItemHandler(matches))
    dispatcher.register(PlaceItemHandler(matches))
