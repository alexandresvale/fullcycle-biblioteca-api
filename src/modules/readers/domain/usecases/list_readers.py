from src.modules.readers.domain.entities import Reader
from src.modules.readers.domain.repositories import ReaderRepository


class ListReadersUseCase:
    """Caso de uso para listagem de leitores cadastrados."""

    def __init__(self, repository: ReaderRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Reader]:
        return self._repository.list_all()
