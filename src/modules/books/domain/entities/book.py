from dataclasses import dataclass
from uuid import UUID, uuid4

from src.core.exceptions import DomainError
from src.modules.books.domain.exceptions import BookUnavailableError

MAX_TITLE_LENGTH = 200
MAX_AUTHOR_LENGTH = 150


def _validate_text(value: object, field_label: str, max_length: int) -> str:
    """Valida e normaliza campos textuais obrigatórios do livro."""
    if not isinstance(value, str):
        raise DomainError(f"{field_label} deve ser um texto.")
    normalized = value.strip()
    if not normalized:
        raise DomainError(f"{field_label} não pode ser vazio.")
    if len(normalized) > max_length:
        raise DomainError(f"{field_label} não pode exceder {max_length} caracteres.")
    return normalized


def _normalize_and_validate_isbn(raw_isbn: object) -> str:
    """Normaliza e valida um código ISBN-10 ou ISBN-13."""
    if not isinstance(raw_isbn, str):
        raise DomainError("ISBN deve ser um texto.")
    normalized = raw_isbn.strip().replace("-", "").replace(" ", "").upper()

    if (
        len(normalized) == 10
        and normalized[:9].isdigit()
        and (normalized[9].isdigit() or normalized[9] == "X")
    ):
        total = sum(
            (10 - idx) * (10 if ch == "X" else int(ch)) for idx, ch in enumerate(normalized)
        )
        if total % 11 == 0:
            return normalized

    if len(normalized) == 13 and normalized.isdigit() and normalized.startswith(("978", "979")):
        total = sum((1 if idx % 2 == 0 else 3) * int(ch) for idx, ch in enumerate(normalized))
        if total % 10 == 0:
            return normalized

    raise DomainError("ISBN inválido. Informe um código ISBN-10 ou ISBN-13 válido.")


def _validate_copy_counts(total_copies: object, available_copies: object) -> tuple[int, int]:
    """Garante as invariantes de quantidade total e disponível de exemplares."""
    if isinstance(total_copies, bool) or not isinstance(total_copies, int):
        raise DomainError("total_copies deve ser um número inteiro.")
    if isinstance(available_copies, bool) or not isinstance(available_copies, int):
        raise DomainError("available_copies deve ser um número inteiro.")
    if total_copies < 1:
        raise DomainError("O livro deve possuir pelo menos 1 exemplar no acervo.")
    if available_copies < 0:
        raise DomainError("available_copies não pode ser negativo.")
    if available_copies > total_copies:
        raise DomainError("available_copies não pode ser maior que total_copies.")
    return total_copies, available_copies


@dataclass(init=False)
class Book:
    """Entidade de domínio representando um livro do acervo."""

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
        self.id = id if id is not None else uuid4()
        self.title = _validate_text(title, "Título", MAX_TITLE_LENGTH)
        self.author = _validate_text(author, "Autor", MAX_AUTHOR_LENGTH)
        self.isbn = _normalize_and_validate_isbn(isbn)
        raw_available = total_copies if available_copies is None else available_copies
        validated_total, validated_available = _validate_copy_counts(total_copies, raw_available)
        self.total_copies = validated_total
        self.available_copies = validated_available
        self._initialized = True

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_initialized", False):
            if name == "title":
                value = _validate_text(value, "Título", MAX_TITLE_LENGTH)
            elif name == "author":
                value = _validate_text(value, "Autor", MAX_AUTHOR_LENGTH)
            elif name == "isbn":
                value = _normalize_and_validate_isbn(value)
            elif name in {"total_copies", "available_copies"}:
                new_total = value if name == "total_copies" else self.total_copies
                new_available = value if name == "available_copies" else self.available_copies
                _validate_copy_counts(new_total, new_available)
        super().__setattr__(name, value)

    def has_available_copy(self) -> bool:
        """Indica se há ao menos um exemplar disponível para empréstimo."""
        return self.available_copies > 0

    def allocate_copy(self) -> None:
        """Reserva um exemplar disponível para empréstimo."""
        if self.available_copies <= 0:
            raise BookUnavailableError("Não há exemplares disponíveis para empréstimo.")
        self.available_copies -= 1

    def reserve_copy(self) -> None:
        """Alias semântico para allocate_copy()."""
        self.allocate_copy()

    def release_copy(self) -> None:
        """Devolve um exemplar ao saldo disponível do acervo."""
        if self.available_copies >= self.total_copies:
            raise DomainError("Todas as cópias do livro já estão disponíveis no acervo.")
        self.available_copies += 1
