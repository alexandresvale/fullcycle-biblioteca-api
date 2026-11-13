from uuid import UUID

from src.modules.books.domain.entities import Book
from src.modules.books.domain.exceptions import BookNotFoundError
from src.modules.books.domain.repositories import BookRepository


class GetBookUseCase:
    """Caso de uso para consulta de um livro específico por ID."""

    def __init__(self, repository: BookRepository) -> None:
        self._repository = repository

    def execute(self, book_id: UUID) -> Book:
        book = self._repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError("Livro não encontrado.")
        return book
