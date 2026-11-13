from src.core.exceptions import ConflictError, DomainError, NotFoundError


class ReaderNotFoundError(NotFoundError):
    """Lançado quando um leitor não é encontrado pelo ID."""


class DuplicateReaderError(ConflictError):
    """Lançado quando já existe leitor cadastrado com o mesmo e-mail ou documento."""


class InactiveReaderError(DomainError):
    """Lançado quando um leitor inativo tenta realizar uma operação restrita."""
