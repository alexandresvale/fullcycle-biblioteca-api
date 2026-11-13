from src.modules.readers.domain.entities import Reader, ReaderCategory
from src.modules.readers.domain.exceptions import DuplicateReaderError
from src.modules.readers.domain.repositories import ReaderRepository


class RegisterReaderUseCase:
    """Caso de uso para cadastro de um novo leitor na biblioteca."""

    def __init__(self, repository: ReaderRepository) -> None:
        self._repository = repository

    def execute(
        self,
        name: str,
        email: str,
        document: str,
        category: ReaderCategory = ReaderCategory.STANDARD,
        active: bool = True,
    ) -> Reader:
        reader = Reader(
            name=name,
            email=email,
            document=document,
            category=category,
            active=active,
        )
        if self._repository.get_by_email(reader.email) is not None:
            raise DuplicateReaderError("Já existe um leitor cadastrado com este e-mail.")
        if self._repository.get_by_document(reader.document) is not None:
            raise DuplicateReaderError("Já existe um leitor cadastrado com este documento.")
        return self._repository.save(reader)
