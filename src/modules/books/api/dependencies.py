from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.books.data.repository import SqlAlchemyBookRepository
from src.modules.books.domain.repositories import BookRepository
from src.modules.books.domain.usecases.get_book import GetBookUseCase
from src.modules.books.domain.usecases.list_books import ListBooksUseCase
from src.modules.books.domain.usecases.register_book import RegisterBookUseCase

DbSession = Annotated[Session, Depends(get_db)]


def get_book_repository(db: DbSession) -> BookRepository:
    return SqlAlchemyBookRepository(db)


BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]


def get_register_book_use_case(repo: BookRepoDep) -> RegisterBookUseCase:
    return RegisterBookUseCase(repo)


RegisterBookUseCaseDep = Annotated[RegisterBookUseCase, Depends(get_register_book_use_case)]


def get_list_books_use_case(repo: BookRepoDep) -> ListBooksUseCase:
    return ListBooksUseCase(repo)


ListBooksUseCaseDep = Annotated[ListBooksUseCase, Depends(get_list_books_use_case)]


def get_get_book_use_case(repo: BookRepoDep) -> GetBookUseCase:
    return GetBookUseCase(repo)


GetBookUseCaseDep = Annotated[GetBookUseCase, Depends(get_get_book_use_case)]
