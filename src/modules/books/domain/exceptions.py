from src.core.exceptions import ConflictError, NotFoundError


class BookUnavailableError(ConflictError):
    """Lançado quando não há exemplares disponíveis para empréstimo."""


class BookNotFoundError(NotFoundError):
    """Lançado quando um livro não é encontrado pelo ID."""


class DuplicateIsbnError(ConflictError):
    """Lançado quando já existe um livro cadastrado com o mesmo ISBN."""
