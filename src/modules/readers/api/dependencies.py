from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.readers.data.repository import SqlAlchemyReaderRepository
from src.modules.readers.domain.repositories import ReaderRepository
from src.modules.readers.domain.usecases.get_reader import GetReaderUseCase
from src.modules.readers.domain.usecases.list_readers import ListReadersUseCase
from src.modules.readers.domain.usecases.register_reader import RegisterReaderUseCase

DbSession = Annotated[Session, Depends(get_db)]


def get_reader_repository(db: DbSession) -> ReaderRepository:
    return SqlAlchemyReaderRepository(db)


ReaderRepoDep = Annotated[ReaderRepository, Depends(get_reader_repository)]


def get_register_reader_use_case(repo: ReaderRepoDep) -> RegisterReaderUseCase:
    return RegisterReaderUseCase(repo)


RegisterReaderUseCaseDep = Annotated[RegisterReaderUseCase, Depends(get_register_reader_use_case)]


def get_get_reader_use_case(repo: ReaderRepoDep) -> GetReaderUseCase:
    return GetReaderUseCase(repo)


GetReaderUseCaseDep = Annotated[GetReaderUseCase, Depends(get_get_reader_use_case)]


def get_list_readers_use_case(repo: ReaderRepoDep) -> ListReadersUseCase:
    return ListReadersUseCase(repo)


ListReadersUseCaseDep = Annotated[ListReadersUseCase, Depends(get_list_readers_use_case)]
