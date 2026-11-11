class DomainError(Exception):
    """Classe base para erros de regra de negocio do dominio."""


class BookUnavailableError(DomainError):
    """Lançado quando não há exemplares disponiveis para empréstimo."""


class LoanLimitExceeded(DomainError):
    """Lançadp quando o leitor atinge  o limiete máximo de emprestimos ativos."""


class LoanAlreadyReturnedError(DomainError):
    """Lançado ao tentar devolver um empréstimo que já foi finalizado."""
