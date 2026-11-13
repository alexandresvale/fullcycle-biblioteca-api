from uuid import UUID, uuid4

import pytest

from src.core.exceptions import ConflictError, DomainError
from src.modules.books.domain.entities.book import Book
from src.modules.books.domain.exceptions import BookUnavailableError
from src.modules.books.domain.repositories.book_repository import BookRepository


class _InMemoryBookRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Book] = {}

    def save(self, book: Book) -> Book:
        self._items[book.id] = book
        return book

    def get_by_id(self, book_id: UUID) -> Book | None:
        return self._items.get(book_id)

    def get_by_isbn(self, isbn: str) -> Book | None:
        return next((b for b in self._items.values() if b.isbn == isbn), None)

    def list_all(self, available_only: bool = False) -> list[Book]:
        books = list(self._items.values())
        if available_only:
            return [b for b in books if b.has_available_copy()]
        return books


def test_create_book_with_valid_isbn13_initializes_available_copies() -> None:
    book = Book(
        title="  Clean Architecture  ",
        author="  Robert C. Martin  ",
        isbn="978-0-13-449416-6",
        total_copies=3,
    )

    assert isinstance(book.id, UUID)
    assert book.title == "Clean Architecture"
    assert book.author == "Robert C. Martin"
    assert book.isbn == "9780134494166"
    assert book.total_copies == 3
    assert book.available_copies == 3
    assert book.has_available_copy() is True


@pytest.mark.parametrize(
    ("raw_isbn", "expected_isbn"),
    [
        ("0132350882", "0132350882"),
        ("0-8044-2957-x", "080442957X"),
        ("978 0 13 235088 4", "9780132350884"),
    ],
)
def test_create_book_normalizes_valid_isbn10_and_isbn13(
    raw_isbn: str,
    expected_isbn: str,
) -> None:
    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn=raw_isbn,
        total_copies=1,
    )
    assert book.isbn == expected_isbn


@pytest.mark.parametrize(
    "invalid_isbn",
    [
        "",
        "12345",
        "9780132350885",
        "0132350883",
        "9770132350887",
        "ABCDEFGHIJ",
    ],
)
def test_invalid_isbn_raises_domain_error(invalid_isbn: str) -> None:
    with pytest.raises(DomainError):
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn=invalid_isbn,
            total_copies=1,
        )


def test_invalid_title_and_author_raise_domain_error() -> None:
    with pytest.raises(DomainError):
        Book(title="   ", author="Autor", isbn="9780132350884", total_copies=1)

    with pytest.raises(DomainError):
        Book(title="T" * 201, author="Autor", isbn="9780132350884", total_copies=1)

    with pytest.raises(DomainError):
        Book(title="Título", author=" ", isbn="9780132350884", total_copies=1)

    with pytest.raises(DomainError):
        Book(title="Título", author="A" * 151, isbn="9780132350884", total_copies=1)


@pytest.mark.parametrize(
    ("total_copies", "available_copies"),
    [
        (0, None),
        (-2, None),
        (2, -1),
        (2, 3),
        (True, None),
        (2, False),
    ],
)
def test_invalid_copy_counts_on_creation_raise_domain_error(
    total_copies: int,
    available_copies: int | None,
) -> None:
    with pytest.raises(DomainError):
        Book(
            title="DDD",
            author="Eric Evans",
            isbn="9780321125217",
            total_copies=total_copies,
            available_copies=available_copies,
        )


def test_reserve_allocate_and_release_copy_lifecycle() -> None:
    book = Book(
        title="Domain-Driven Design",
        author="Eric Evans",
        isbn="9780321125217",
        total_copies=2,
    )

    book.reserve_copy()
    assert book.available_copies == 1
    assert book.has_available_copy() is True

    book.allocate_copy()
    assert book.available_copies == 0
    assert book.has_available_copy() is False

    with pytest.raises(BookUnavailableError) as exc_info:
        book.reserve_copy()
    assert isinstance(exc_info.value, ConflictError)

    book.release_copy()
    assert book.available_copies == 1
    book.release_copy()
    assert book.available_copies == 2

    with pytest.raises(DomainError):
        book.release_copy()


def test_encapsulation_prevents_invalid_direct_copy_mutation() -> None:
    book = Book(
        title="Refactoring",
        author="Martin Fowler",
        isbn="9780134757599",
        total_copies=2,
        available_copies=1,
        id=uuid4(),
    )

    with pytest.raises(DomainError):
        book.available_copies = -1
    assert book.available_copies == 1

    with pytest.raises(DomainError):
        book.available_copies = 3
    assert book.available_copies == 1

    with pytest.raises(DomainError):
        book.total_copies = 0
    assert book.total_copies == 2

    with pytest.raises(DomainError):
        book.available_copies = True  # type: ignore[assignment]
    assert book.available_copies == 1


def test_encapsulation_protects_title_author_and_isbn_mutations() -> None:
    book = Book(
        title="Refactoring",
        author="Martin Fowler",
        isbn="9780134757599",
        total_copies=2,
    )

    book.title = "  Refactoring (2nd Ed.)  "
    book.author = "  Martin Fowler  "
    book.isbn = "978-0-13-235088-4"
    assert book.title == "Refactoring (2nd Ed.)"
    assert book.author == "Martin Fowler"
    assert book.isbn == "9780132350884"

    with pytest.raises(DomainError):
        book.title = "   "
    assert book.title == "Refactoring (2nd Ed.)"

    with pytest.raises(DomainError):
        book.title = 123  # type: ignore[assignment]
    assert book.title == "Refactoring (2nd Ed.)"

    with pytest.raises(DomainError):
        book.author = ""
    assert book.author == "Martin Fowler"

    with pytest.raises(DomainError):
        book.isbn = "invalid-isbn"
    assert book.isbn == "9780132350884"

    with pytest.raises(DomainError):
        book.isbn = 9780132350884  # type: ignore[assignment]
    assert book.isbn == "9780132350884"


def test_book_repository_protocol_structural_compatibility() -> None:
    repo: BookRepository = _InMemoryBookRepository()
    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        total_copies=1,
    )
    repo.save(book)
    assert repo.get_by_id(book.id) == book
    assert repo.get_by_isbn("9780132350884") == book
    assert repo.list_all(available_only=True) == [book]
