from uuid import UUID, uuid4

import pytest

from src.modules.books.domain.entities import Book
from src.modules.books.domain.exceptions import BookNotFoundError, DuplicateIsbnError
from src.modules.books.domain.usecases.get_book import GetBookUseCase
from src.modules.books.domain.usecases.list_books import ListBooksUseCase
from src.modules.books.domain.usecases.register_book import RegisterBookUseCase


class InMemoryBookRepository:
    def __init__(self) -> None:
        self._books: dict[UUID, Book] = {}

    def save(self, book: Book) -> Book:
        self._books[book.id] = book
        return book

    def get_by_id(self, book_id: UUID) -> Book | None:
        return self._books.get(book_id)

    def get_by_isbn(self, isbn: str) -> Book | None:
        return next((book for book in self._books.values() if book.isbn == isbn), None)

    def list_all(self, *, available_only: bool = False) -> list[Book]:
        books = list(self._books.values())
        if available_only:
            books = [book for book in books if book.has_available_copy()]
        return books


def test_register_and_get_book_use_cases() -> None:
    repo = InMemoryBookRepository()
    register_uc = RegisterBookUseCase(repo)
    get_uc = GetBookUseCase(repo)

    created = register_uc.execute(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="978-0-13-235088-4",
        total_copies=4,
    )

    assert created.isbn == "9780132350884"
    assert created.available_copies == 4

    fetched = get_uc.execute(created.id)
    assert fetched == created


def test_register_duplicate_isbn_raises_conflict() -> None:
    repo = InMemoryBookRepository()
    register_uc = RegisterBookUseCase(repo)

    register_uc.execute("Clean Code", "Robert C. Martin", "978-0-13-235088-4", 2)

    with pytest.raises(DuplicateIsbnError):
        register_uc.execute("Clean Code 2nd Ed", "Robert C. Martin", "9780132350884", 1)


def test_list_books_supports_available_only_filter() -> None:
    repo = InMemoryBookRepository()
    register_uc = RegisterBookUseCase(repo)
    list_uc = ListBooksUseCase(repo)

    b1 = register_uc.execute("Book 1", "Author 1", "9780132350884", 1)
    b2 = register_uc.execute("Book 2", "Author 2", "9780134494166", 2)
    b1.allocate_copy()
    repo.save(b1)

    assert len(list_uc.execute()) == 2
    available = list_uc.execute(available_only=True)
    assert available == [b2]


def test_get_nonexistent_book_raises_not_found() -> None:
    repo = InMemoryBookRepository()
    get_uc = GetBookUseCase(repo)

    with pytest.raises(BookNotFoundError):
        get_uc.execute(uuid4())
