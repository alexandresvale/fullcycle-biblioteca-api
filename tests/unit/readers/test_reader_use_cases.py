from uuid import UUID, uuid4

import pytest

from src.modules.readers.domain.entities import Reader, ReaderCategory
from src.modules.readers.domain.exceptions import DuplicateReaderError, ReaderNotFoundError
from src.modules.readers.domain.usecases.get_reader import GetReaderUseCase
from src.modules.readers.domain.usecases.list_readers import ListReadersUseCase
from src.modules.readers.domain.usecases.register_reader import RegisterReaderUseCase


class InMemoryReaderRepository:
    def __init__(self) -> None:
        self._readers: dict[UUID, Reader] = {}

    def save(self, reader: Reader) -> Reader:
        self._readers[reader.id] = reader
        return reader

    def get_by_id(self, reader_id: UUID) -> Reader | None:
        return self._readers.get(reader_id)

    def get_by_email(self, email: str) -> Reader | None:
        return next((r for r in self._readers.values() if r.email == email), None)

    def get_by_document(self, document: str) -> Reader | None:
        return next((r for r in self._readers.values() if r.document == document), None)

    def list_all(self) -> list[Reader]:
        return list(self._readers.values())


def test_register_list_and_get_reader_use_cases() -> None:
    repo = InMemoryReaderRepository()
    register_uc = RegisterReaderUseCase(repo)
    get_uc = GetReaderUseCase(repo)
    list_uc = ListReadersUseCase(repo)

    created = register_uc.execute(
        name="Ricardo Vale",
        email="Ricardo@Example.com",
        document="111.222.333-44",
        category=ReaderCategory.ACADEMIC,
    )

    assert created.email == "ricardo@example.com"
    assert created.document == "11122233344"
    assert created.category == ReaderCategory.ACADEMIC

    assert get_uc.execute(created.id) == created
    assert list_uc.execute() == [created]


def test_register_duplicate_email_or_document_raises_conflict() -> None:
    repo = InMemoryReaderRepository()
    register_uc = RegisterReaderUseCase(repo)

    register_uc.execute("Maria Silva", "maria@example.com", "111.222.333-44")

    with pytest.raises(DuplicateReaderError):
        register_uc.execute("Maria S.", "MARIA@example.com", "999.888.777-66")

    with pytest.raises(DuplicateReaderError):
        register_uc.execute("Outro Leitor", "outro@example.com", "11122233344")


def test_get_nonexistent_reader_raises_not_found() -> None:
    repo = InMemoryReaderRepository()
    get_uc = GetReaderUseCase(repo)

    with pytest.raises(ReaderNotFoundError):
        get_uc.execute(uuid4())
