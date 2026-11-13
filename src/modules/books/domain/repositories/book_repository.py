from typing import Protocol
from uuid import UUID

from src.modules.books.domain.entities.book import Book


class BookRepository(Protocol):
    """Contrato de persistência para livros do acervo (DIP - SOLID)."""

    def save(self, book: Book) -> Book: ...

    def get_by_id(self, book_id: UUID) -> Book | None: ...

    def get_by_isbn(self, isbn: str) -> Book | None: ...

    def list_all(self, available_only: bool = False) -> list[Book]: ...
