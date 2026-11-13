from src.modules.books.domain.entities import Book
from src.modules.books.domain.repositories import BookRepository


class ListBooksUseCase:
    """Caso de uso para listagem de livros do acervo."""

    def __init__(self, repository: BookRepository) -> None:
        self._repository = repository

    def execute(self, *, available_only: bool = False) -> list[Book]:
        return self._repository.list_all(available_only=available_only)
