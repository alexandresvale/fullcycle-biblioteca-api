from src.core.exceptions import ConflictError, DomainError, NotFoundError


class BookUnavailableError(ConflictError):
    """Lançado quando não há exemplares disponíveis para empréstimo."""


class LoanLimitExceededError(DomainError):
    """Lançado quando o leitor atinge o limite máximo de empréstimos ativos."""


class LoanAlreadyReturnedError(ConflictError):
    """Lançado ao tentar devolver um empréstimo que já foi finalizado."""


class LoanNotFoundError(NotFoundError):
    """Lançado quando um empréstimo não é encontrado pelo ID."""
