from onair.core.errors import ConflictError, UnauthorizedError
from onair.core.security import PasswordHasher, TokenService
from onair.modules.auth.application.dto import TokenPair
from onair.modules.players.domain.player import Player
from onair.modules.players.domain.repository import PlayerRepository


class TokenPairIssuer:
    def __init__(self, tokens: TokenService) -> None:
        self._tokens = tokens

    def issue(self, player: Player) -> TokenPair:
        return TokenPair(
            player_id=player.id,
            access_token=self._tokens.issue(player.id, "access"),
            refresh_token=self._tokens.issue(player.id, "refresh"),
        )


class RegisterPlayer:
    def __init__(
        self, players: PlayerRepository, hasher: PasswordHasher, issuer: TokenPairIssuer
    ) -> None:
        self._players = players
        self._hasher = hasher
        self._issuer = issuer

    async def execute(self, *, username: str, email: str, password: str) -> TokenPair:
        if await self._players.exists(username=username, email=email):
            raise ConflictError("Username or email already in use")
        player = Player(username=username, email=email, password_hash=self._hasher.hash(password))
        await self._players.add(player)
        return self._issuer.issue(player)


class Login:
    def __init__(
        self, players: PlayerRepository, hasher: PasswordHasher, issuer: TokenPairIssuer
    ) -> None:
        self._players = players
        self._hasher = hasher
        self._issuer = issuer

    async def execute(self, *, username: str, password: str) -> TokenPair:
        player = await self._players.get_by_username(username)
        if player is None or not self._hasher.verify(password, player.password_hash):
            raise UnauthorizedError("Invalid credentials")
        return self._issuer.issue(player)


class RefreshTokens:
    def __init__(
        self, players: PlayerRepository, tokens: TokenService, issuer: TokenPairIssuer
    ) -> None:
        self._players = players
        self._tokens = tokens
        self._issuer = issuer

    async def execute(self, refresh_token: str) -> TokenPair:
        player_id = self._tokens.verify(refresh_token, "refresh")
        player = await self._players.get(player_id)
        if player is None:
            raise UnauthorizedError("Player no longer exists")
        return self._issuer.issue(player)
