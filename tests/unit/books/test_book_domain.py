import pytest

from src.core.exceptions import DomainError
from src.modules.books.domain.entities import Book
from src.modules.books.domain.exceptions import BookUnavailableError


def test_book_initializes_available_copies_equal_to_total_and_normalizes_isbn() -> None:
    book = Book(
        title="  Clean Architecture  ",
        author="  Robert C. Martin  ",
        isbn="978-0-13-449416-6",
        total_copies=3,
    )

    assert book.title == "Clean Architecture"
    assert book.author == "Robert C. Martin"
    assert book.isbn == "9780134494166"
    assert book.total_copies == 3
    assert book.available_copies == 3
    assert book.has_available_copy() is True


def test_book_accepts_isbn_10_with_trailing_x() -> None:
    book = Book(
        title="Domain-Driven Design",
        author="Eric Evans",
        isbn="0-321-12521-x",
        total_copies=1,
    )
    assert book.isbn == "032112521X"


def test_book_allocate_and_release_copy() -> None:
    book = Book(
        title="Refactoring",
        author="Martin Fowler",
        isbn="9780134757599",
        total_copies=1,
    )

    book.allocate_copy()
    assert book.available_copies == 0
    assert book.has_available_copy() is False

    with pytest.raises(BookUnavailableError):
        book.allocate_copy()

    book.release_copy()
    assert book.available_copies == 1

    with pytest.raises(DomainError):
        book.release_copy()


@pytest.mark.parametrize(
    ("title", "author", "isbn", "total_copies", "available_copies"),
    [
        ("", "Author", "9780134494166", 1, None),
        ("A" * 201, "Author", "9780134494166", 1, None),
        ("Title", "   ", "9780134494166", 1, None),
        ("Title", "A" * 151, "9780134494166", 1, None),
        ("Title", "Author", "12345", 1, None),
        ("Title", "Author", "9780134494166", 0, None),
        ("Title", "Author", "9780134494166", 2, -1),
        ("Title", "Author", "9780134494166", 2, 3),
    ],
)
def test_book_invariants_raise_domain_error(
    title: str,
    author: str,
    isbn: str,
    total_copies: int,
    available_copies: int | None,
) -> None:
    with pytest.raises(DomainError):
        Book(
            title=title,
            author=author,
            isbn=isbn,
            total_copies=total_copies,
            available_copies=available_copies,
        )
