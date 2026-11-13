from src.core.exceptions import ConflictError, NotFoundError


class BookNotFoundError(NotFoundError):
    """Lançado quando um livro não é encontrado pelo ID."""


class DuplicateIsbnError(ConflictError):
    """Lançado ao tentar cadastrar um livro com ISBN já existente no acervo."""


class BookUnavailableError(ConflictError):
    """Lançado quando não há exemplares disponíveis para alocação."""
