from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

import jwt
from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

from onair.core.errors import UnauthorizedError

TokenKind = Literal["access", "refresh"]


class PasswordHasher:
    def __init__(self) -> None:
        self._hasher = Argon2Hasher()

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except VerifyMismatchError:
            return False


class TokenService:
    def __init__(
        self, secret: str, algorithm: str, access_ttl_seconds: int, refresh_ttl_seconds: int
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._ttl: dict[TokenKind, int] = {
            "access": access_ttl_seconds,
            "refresh": refresh_ttl_seconds,
        }

    def issue(self, subject: UUID, kind: TokenKind) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(subject),
            "kind": kind,
            "iat": now,
            "exp": now + timedelta(seconds=self._ttl[kind]),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify(self, token: str, expected_kind: TokenKind) -> UUID:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid token") from exc
        if payload.get("kind") != expected_kind:
            raise UnauthorizedError("Wrong token kind")
        return UUID(payload["sub"])
