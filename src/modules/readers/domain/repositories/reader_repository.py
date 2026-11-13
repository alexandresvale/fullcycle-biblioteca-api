from typing import Protocol
from uuid import UUID

from src.modules.readers.domain.entities.reader import Reader


class ReaderRepository(Protocol):
    """Contrato de persistência para leitores (DIP - SOLID)."""

    def save(self, reader: Reader) -> Reader: ...

    def get_by_id(self, reader_id: UUID) -> Reader | None: ...

    def get_by_email(self, email: str) -> Reader | None: ...

    def get_by_document(self, document: str) -> Reader | None: ...

    def list_all(self) -> list[Reader]: ...
