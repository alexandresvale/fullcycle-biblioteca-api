from uuid import UUID

import pytest

from src.core.exceptions import DomainError
from src.modules.readers.domain.entities.reader import Reader, ReaderCategory
from src.modules.readers.domain.exceptions import InactiveReaderError
from src.modules.readers.domain.repositories.reader_repository import ReaderRepository


class _InMemoryReaderRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Reader] = {}

    def save(self, reader: Reader) -> Reader:
        self._items[reader.id] = reader
        return reader

    def get_by_id(self, reader_id: UUID) -> Reader | None:
        return self._items.get(reader_id)

    def get_by_email(self, email: str) -> Reader | None:
        return next((r for r in self._items.values() if r.email == email), None)

    def get_by_document(self, document: str) -> Reader | None:
        return next((r for r in self._items.values() if r.document == document), None)

    def list_all(self) -> list[Reader]:
        return list(self._items.values())


def test_create_standard_reader_normalizes_fields() -> None:
    reader = Reader(
        name="  Maria Silva  ",
        email="  MARIA.Silva@Example.COM ",
        document="123.456.789-01",
    )

    assert isinstance(reader.id, UUID)
    assert reader.name == "Maria Silva"
    assert reader.email == "maria.silva@example.com"
    assert reader.document == "12345678901"
    assert reader.category == ReaderCategory.STANDARD
    assert reader.active is True
    assert reader.is_academic() is False


def test_create_academic_reader() -> None:
    reader = Reader(
        name="Prof. João Souza",
        email="joao@universidade.edu.br",
        document="mat-2026001",
        category=ReaderCategory.ACADEMIC,
    )

    assert reader.category == ReaderCategory.ACADEMIC
    assert reader.document == "MAT2026001"
    assert reader.is_academic() is True


@pytest.mark.parametrize("invalid_name", ["", "  ", "Jo"])
def test_invalid_reader_name_raises_domain_error(invalid_name: str) -> None:
    with pytest.raises(DomainError):
        Reader(
            name=invalid_name,
            email="leitor@exemplo.com",
            document="12345678901",
        )


@pytest.mark.parametrize(
    "invalid_email",
    [
        "",
        "sem-arroba.com",
        "usuario@",
        "@dominio.com",
        "usuario@dominio",
        "usuario @dominio.com",
        "a@b..c",
        "a@b.c.",
        ".ana@exemplo.com",
        "ana.@exemplo.com",
        "a@b.c",
    ],
)
def test_invalid_reader_email_raises_domain_error(invalid_email: str) -> None:
    with pytest.raises(DomainError):
        Reader(
            name="Ana Costa",
            email=invalid_email,
            document="12345678901",
        )


@pytest.mark.parametrize("invalid_document", ["", ".-/", "12", "???", "A" * 31])
def test_invalid_reader_document_raises_domain_error(invalid_document: str) -> None:
    with pytest.raises(DomainError):
        Reader(
            name="Ana Costa",
            email="ana@exemplo.com",
            document=invalid_document,
        )


def test_invalid_reader_category_and_non_str_types_raise_domain_error() -> None:
    with pytest.raises(DomainError):
        Reader(
            name="Ana Costa",
            email="ana@exemplo.com",
            document="12345678901",
            category="VIP",  # type: ignore[arg-type]
        )

    with pytest.raises(DomainError):
        Reader(
            name="Ana Costa",
            email="ana@exemplo.com",
            document="12345678901",
            category=123,  # type: ignore[arg-type]
        )

    with pytest.raises(DomainError):
        Reader(
            name=123,  # type: ignore[arg-type]
            email="ana@exemplo.com",
            document="12345678901",
        )

    with pytest.raises(DomainError):
        Reader(
            name="Ana Costa",
            email=123,  # type: ignore[arg-type]
            document="12345678901",
        )

    with pytest.raises(DomainError):
        Reader(
            name="Ana Costa",
            email="ana@exemplo.com",
            document=123,  # type: ignore[arg-type]
        )


def test_reader_encapsulation_protects_direct_mutations() -> None:
    reader = Reader(
        name="Ana Costa",
        email="ana@exemplo.com",
        document="123.456.789-01",
    )

    reader.name = "  Ana Maria Costa  "
    reader.email = "  ANA.MARIA@Exemplo.COM "
    reader.document = "mat-2026/02"
    reader.category = ReaderCategory.ACADEMIC
    assert reader.name == "Ana Maria Costa"
    assert reader.email == "ana.maria@exemplo.com"
    assert reader.document == "MAT202602"
    assert reader.is_academic() is True

    with pytest.raises(DomainError):
        reader.name = "Ab"
    assert reader.name == "Ana Maria Costa"

    with pytest.raises(DomainError):
        reader.email = "invalido"
    assert reader.email == "ana.maria@exemplo.com"

    with pytest.raises(DomainError):
        reader.document = "???"
    assert reader.document == "MAT202602"

    with pytest.raises(DomainError):
        reader.category = "VIP"  # type: ignore[assignment]
    assert reader.category == ReaderCategory.ACADEMIC

    with pytest.raises(DomainError):
        reader.active = "sim"  # type: ignore[assignment]
    assert reader.active is True


def test_reader_activation_lifecycle() -> None:
    reader = Reader(
        name="Carlos Lima",
        email="carlos@exemplo.com",
        document="98765432100",
    )

    reader.ensure_active()
    reader.deactivate()
    assert reader.active is False

    with pytest.raises(InactiveReaderError):
        reader.ensure_active()

    reader.activate()
    assert reader.active is True
    reader.ensure_active()


def test_reader_repository_protocol_structural_compatibility() -> None:
    repo: ReaderRepository = _InMemoryReaderRepository()
    reader = Reader(
        name="Carlos Lima",
        email="carlos@exemplo.com",
        document="98765432100",
    )
    repo.save(reader)
    assert repo.get_by_id(reader.id) == reader
    assert repo.get_by_email("carlos@exemplo.com") == reader
    assert repo.get_by_document("98765432100") == reader
    assert repo.list_all() == [reader]
