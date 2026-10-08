class DomainError(Exception):
    """Base for business-rule violations; mapped to HTTP/WS errors at the edges."""

    code: str = "domain_error"
    status_code: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404


class ConflictError(DomainError):
    code = "conflict"
    status_code = 409


class UnauthorizedError(DomainError):
    code = "unauthorized"
    status_code = 401
