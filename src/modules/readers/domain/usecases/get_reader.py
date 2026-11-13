from uuid import UUID

from src.modules.readers.domain.entities import Reader
from src.modules.readers.domain.exceptions import ReaderNotFoundError
from src.modules.readers.domain.repositories import ReaderRepository


class GetReaderUseCase:
    """Caso de uso para consulta de um leitor específico por ID."""

    def __init__(self, repository: ReaderRepository) -> None:
        self._repository = repository

    def execute(self, reader_id: UUID) -> Reader:
        reader = self._repository.get_by_id(reader_id)
        if reader is None:
            raise ReaderNotFoundError("Leitor não encontrado.")
        return reader
