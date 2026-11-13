import re
from dataclasses import dataclass
from uuid import UUID, uuid4

from src.core.exceptions import DomainError
from src.modules.books.domain.exceptions import BookUnavailableError

_ISBN_10_RE = re.compile(r"^\d{9}[\dX]$")
_ISBN_13_RE = re.compile(r"^\d{13}$")


def normalize_isbn(raw_isbn: str) -> str:
    """Normaliza e valida ISBN-10 ou ISBN-13 removendo hífens e espaços."""
    normalized = re.sub(r"[\s-]+", "", raw_isbn).upper()
    if not (_ISBN_10_RE.match(normalized) or _ISBN_13_RE.match(normalized)):
        raise DomainError("ISBN inválido: informe um código ISBN-10 ou ISBN-13 válido.")
    return normalized


@dataclass(init=False)
class Book:
    """Entidade de domínio representando um livro do acervo da biblioteca."""

    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int
    id: UUID

    def __init__(
        self,
        title: str,
        author: str,
        isbn: str,
        total_copies: int,
        available_copies: int | None = None,
        id: UUID | None = None,
    ) -> None:
        self.title = title.strip()
        self.author = author.strip()
        self.isbn = normalize_isbn(isbn)
        self.total_copies = total_copies
        self.available_copies = total_copies if available_copies is None else available_copies
        self.id = uuid4() if id is None else id
        self._validate()

    def _validate(self) -> None:
        if not self.title or len(self.title) > 200:
            raise DomainError("Título do livro deve ter entre 1 e 200 caracteres.")
        if not self.author or len(self.author) > 150:
            raise DomainError("Nome do autor deve ter entre 1 e 150 caracteres.")
        if self.total_copies < 1:
            raise DomainError("Quantidade total de exemplares deve ser pelo menos 1.")
        if self.available_copies < 0 or self.available_copies > self.total_copies:
            raise DomainError("Exemplares disponíveis devem estar entre 0 e o total de exemplares.")

    def has_available_copy(self) -> bool:
        """Indica se há pelo menos um exemplar disponível para empréstimo."""
        return self.available_copies > 0

    def allocate_copy(self) -> None:
        """Reserva um exemplar disponível para empréstimo."""
        if not self.has_available_copy():
            raise BookUnavailableError("Não há exemplares disponíveis para este livro.")
        self.available_copies -= 1

    def release_copy(self) -> None:
        """Devolve um exemplar ao saldo disponível do acervo."""
        if self.available_copies >= self.total_copies:
            raise DomainError("Todos os exemplares deste livro já estão disponíveis.")
        self.available_copies += 1
