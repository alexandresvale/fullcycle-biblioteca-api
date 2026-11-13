from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateBookRequest(BaseModel):
    """Schema de requisição para cadastro de livro no acervo."""

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=150)
    isbn: str = Field(min_length=1, max_length=32)
    total_copies: int = Field(ge=1)


class BookResponse(BaseModel):
    """Schema de resposta com os dados de um livro do acervo."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int
