from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.modules.readers.data.model import ReaderModel
from src.modules.readers.domain.entities import Reader, ReaderCategory
from src.modules.readers.domain.exceptions import DuplicateReaderError


class SqlAlchemyReaderRepository:
    """Implementação concreta do ReaderRepository com PostgreSQL + SQLAlchemy 2.0."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, reader: Reader) -> Reader:
        model = self._session.get(ReaderModel, reader.id)
        if model is None:
            model = ReaderModel(
                id=reader.id,
                name=reader.name,
                email=reader.email,
                document=reader.document,
                category=reader.category.value,
                active=reader.active,
            )
            self._session.add(model)
        else:
            model.name = reader.name
            model.email = reader.email
            model.document = reader.document
            model.category = reader.category.value
            model.active = reader.active

        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise DuplicateReaderError(
                "Já existe um leitor cadastrado com este e-mail ou documento."
            ) from exc

        return reader

    def get_by_id(self, reader_id: UUID) -> Reader | None:
        model = self._session.get(ReaderModel, reader_id)
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_email(self, email: str) -> Reader | None:
        stmt = select(ReaderModel).where(ReaderModel.email == email)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_document(self, document: str) -> Reader | None:
        stmt = select(ReaderModel).where(ReaderModel.document == document)
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def list_all(self) -> list[Reader]:
        stmt = select(ReaderModel).order_by(ReaderModel.name.asc())
        models = self._session.scalars(stmt).all()
        return [self._to_entity(model) for model in models]

    @staticmethod
    def _to_entity(model: ReaderModel) -> Reader:
        return Reader(
            id=model.id,
            name=model.name,
            email=model.email,
            document=model.document,
            category=ReaderCategory(model.category),
            active=model.active,
        )
