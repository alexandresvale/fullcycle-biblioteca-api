from src.modules.books.domain.entities import Book
from src.modules.books.domain.exceptions import DuplicateIsbnError
from src.modules.books.domain.repositories import BookRepository


class RegisterBookUseCase:
    """Caso de uso para cadastro de um novo livro no acervo."""

    def __init__(self, repository: BookRepository) -> None:
        self._repository = repository

    def execute(self, title: str, author: str, isbn: str, total_copies: int) -> Book:
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            total_copies=total_copies,
        )
        if self._repository.get_by_isbn(book.isbn) is not None:
            raise DuplicateIsbnError(f"Já existe um livro cadastrado com o ISBN {book.isbn}.")
        return self._repository.save(book)
