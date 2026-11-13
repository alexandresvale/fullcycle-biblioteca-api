from src.core.exceptions import ConflictError, DomainError, NotFoundError


class ReaderNotFoundError(NotFoundError):
    """Lançado quando um leitor não é encontrado pelo ID."""


class DuplicateReaderError(ConflictError):
    """Lançado ao tentar cadastrar um leitor com e-mail ou documento já existente."""


class InactiveReaderError(DomainError):
    """Lançado quando um leitor inativo tenta realizar uma operação restrita."""
