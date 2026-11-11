class DomainError(Exception):
    """Classe base para erros de regra de negócio do domínio."""


class NotFoundError(DomainError):
    """Classe base para recursos não encontrados (mapeado para HTTP 404)."""


class ConflictError(DomainError):
    """Classe base para conflitos de estado de negócio (mapeado para HTTP 409)."""
