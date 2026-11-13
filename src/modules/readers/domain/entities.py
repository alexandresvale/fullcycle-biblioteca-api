import re
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from src.core.exceptions import DomainError
from src.modules.readers.domain.exceptions import InactiveReaderError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ReaderCategory(StrEnum):
    """Categorias de perfil de leitor suportadas pela biblioteca."""

    STANDARD = "STANDARD"
    ACADEMIC = "ACADEMIC"


def normalize_document(raw_document: str) -> str:
    """Normaliza documento (CPF ou matrícula) removendo pontuação e espaços."""
    normalized = re.sub(r"[\s.\-/]+", "", raw_document).upper()
    if len(normalized) < 3 or len(normalized) > 30:
        raise DomainError("Documento do leitor deve ter entre 3 e 30 caracteres válidos.")
    return normalized


@dataclass(init=False)
class Reader:
    """Entidade de domínio representando um leitor cadastrado na biblioteca."""

    name: str
    email: str
    document: str
    category: ReaderCategory
    active: bool
    id: UUID

    def __init__(
        self,
        name: str,
        email: str,
        document: str,
        category: ReaderCategory = ReaderCategory.STANDARD,
        active: bool = True,
        id: UUID | None = None,
    ) -> None:
        self.name = name.strip()
        self.email = email.strip().lower()
        self.document = normalize_document(document)
        self.category = category
        self.active = active
        self.id = uuid4() if id is None else id
        self._validate()

    def _validate(self) -> None:
        if len(self.name) < 3 or len(self.name) > 150:
            raise DomainError("Nome do leitor deve ter entre 3 e 150 caracteres.")
        if not _EMAIL_RE.match(self.email) or len(self.email) > 255:
            raise DomainError("E-mail do leitor é inválido.")

    def deactivate(self) -> None:
        """Desativa o cadastro do leitor."""
        self.active = False

    def activate(self) -> None:
        """Reativa o cadastro do leitor."""
        self.active = True

    def ensure_active(self) -> None:
        """Garante que o leitor está ativo para realizar operações."""
        if not self.active:
            raise InactiveReaderError("Leitor inativo não pode realizar novos empréstimos.")
