from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.modules.books.data.model import BookModel
from src.modules.books.domain.entities import Book
from src.modules.books.domain.exceptions import DuplicateIsbnError


class SqlAlchemyBookRepository:
    """Implementação concreta do BookRepository com PostgreSQL + SQLAlchemy 2.0."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, book: Book) -> Book:
        model = self._session.get(BookModel, book.id)
        if model is None:
            model = BookModel(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                total_copies=book.total_copies,
                available_copies=book.available_copies,
            )
            self._session.add(model)
        else:
            model.title = book.title
            model.author = book.author
            model.isbn = book.isbn
            model.total_copies = book.total_copies
            model.available_copies = book.available_copies

        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateIsbnError(
                f"Já existe um livro cadastrado com o ISBN {book.isbn}."
            ) from exc

        return book

    def get_by_id(self, book_id: UUID) -> Book | None:
        model = self._session.get(BookModel, book_id)
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_isbn(self, isbn: str) -> Book | None:
        stmt = select(BookModel).where(BookModel.isbn == isbn)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self, *, available_only: bool = False) -> list[Book]:
        stmt = select(BookModel)
        if available_only:
            stmt = stmt.where(BookModel.available_copies > 0)
        stmt = stmt.order_by(BookModel.title.asc())
        models = self._session.scalars(stmt).all()
        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: BookModel) -> Book:
        return Book(
            id=model.id,
            title=model.title,
            author=model.author,
            isbn=model.isbn,
            total_copies=model.total_copies,
            available_copies=model.available_copies,
        )
