import re
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from src.core.exceptions import DomainError
from src.modules.readers.domain.exceptions import InactiveReaderError

MIN_READER_NAME_LENGTH = 3
MIN_DOCUMENT_LENGTH = 3
MAX_DOCUMENT_LENGTH = 30
_EMAIL_PATTERN = re.compile(r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$")


class ReaderCategory(StrEnum):
    """Perfil do leitor para integração com a estratégia de multa."""

    STANDARD = "STANDARD"
    ACADEMIC = "ACADEMIC"


def _validate_name(raw_name: object) -> str:
    """Valida e normaliza o nome do leitor."""
    if not isinstance(raw_name, str):
        raise DomainError("Nome do leitor deve ser um texto.")
    normalized = raw_name.strip()
    if len(normalized) < MIN_READER_NAME_LENGTH:
        raise DomainError(
            f"Nome do leitor deve ter pelo menos {MIN_READER_NAME_LENGTH} caracteres."
        )
    return normalized


def _validate_email(raw_email: object) -> str:
    """Valida e normaliza o e-mail do leitor."""
    if not isinstance(raw_email, str):
        raise DomainError("E-mail do leitor deve ser um texto.")
    normalized = raw_email.strip().lower()
    local_part = normalized.partition("@")[0]
    if (
        ".." in normalized
        or local_part.startswith(".")
        or local_part.endswith(".")
        or not _EMAIL_PATTERN.match(normalized)
    ):
        raise DomainError("E-mail do leitor é inválido.")
    return normalized


def _validate_document(raw_document: object) -> str:
    """Valida e normaliza o documento (CPF ou matrícula institucional)."""
    if not isinstance(raw_document, str):
        raise DomainError("Documento do leitor deve ser um texto.")
    normalized = re.sub(r"[.\-/\s]", "", raw_document).upper()
    if (
        len(normalized) < MIN_DOCUMENT_LENGTH
        or len(normalized) > MAX_DOCUMENT_LENGTH
        or not normalized.isalnum()
    ):
        raise DomainError("Documento do leitor é inválido.")
    return normalized


def _validate_category(raw_category: object) -> ReaderCategory:
    """Valida e converte a categoria do leitor."""
    if isinstance(raw_category, ReaderCategory):
        return raw_category
    if isinstance(raw_category, str):
        try:
            return ReaderCategory(raw_category)
        except ValueError as exc:
            raise DomainError("Tipo de leitor inválido. Use STANDARD ou ACADEMIC.") from exc
    raise DomainError("Tipo de leitor inválido. Use STANDARD ou ACADEMIC.")


def _validate_active(raw_active: object) -> bool:
    """Valida o indicador booleano de atividade do leitor."""
    if not isinstance(raw_active, bool):
        raise DomainError("O campo active deve ser um booleano.")
    return raw_active


@dataclass
class Reader:
    """Entidade de domínio representando um leitor cadastrado na biblioteca."""

    name: str
    email: str
    document: str
    category: ReaderCategory = ReaderCategory.STANDARD
    active: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = _validate_name(self.name)
        self.email = _validate_email(self.email)
        self.document = _validate_document(self.document)
        self.category = _validate_category(self.category)
        self.active = _validate_active(self.active)
        self._initialized = True

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_initialized", False):
            if name == "name":
                value = _validate_name(value)
            elif name == "email":
                value = _validate_email(value)
            elif name == "document":
                value = _validate_document(value)
            elif name == "category":
                value = _validate_category(value)
            elif name == "active":
                value = _validate_active(value)
        super().__setattr__(name, value)

    def is_academic(self) -> bool:
        """Indica se o leitor possui perfil acadêmico."""
        return self.category == ReaderCategory.ACADEMIC

    def activate(self) -> None:
        """Reativa o cadastro do leitor."""
        self.active = True

    def deactivate(self) -> None:
        """Inativa o cadastro do leitor."""
        self.active = False

    def ensure_active(self) -> None:
        """Garante que o leitor está ativo para realizar novos empréstimos."""
        if not self.active:
            raise InactiveReaderError("Leitor inativo não pode realizar novos empréstimos.")
