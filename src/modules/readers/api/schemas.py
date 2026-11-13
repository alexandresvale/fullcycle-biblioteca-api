from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.modules.readers.domain.entities import ReaderCategory


class CreateReaderRequest(BaseModel):
    """Schema de requisição para cadastro de leitor."""

    name: str = Field(min_length=3, max_length=150)
    email: str = Field(min_length=3, max_length=255)
    document: str = Field(min_length=3, max_length=30)
    category: ReaderCategory = ReaderCategory.STANDARD
    active: bool = True


class ReaderResponse(BaseModel):
    """Schema de resposta com os dados de um leitor cadastrado."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    document: str
    category: ReaderCategory
    active: bool
