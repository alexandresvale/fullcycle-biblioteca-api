from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.core.database import SessionLocal
from src.main import app
from src.modules.books.data.repository import SqlAlchemyBookRepository
from src.modules.books.domain.entities import Book
from src.modules.books.domain.exceptions import DuplicateIsbnError
from src.modules.readers.data.repository import SqlAlchemyReaderRepository
from src.modules.readers.domain.entities import Reader, ReaderCategory
from src.modules.readers.domain.exceptions import DuplicateReaderError


def _unique_isbn() -> str:
    return f"978{uuid4().int % 10_000_000_000:010d}"


def _unique_document() -> str:
    return f"{uuid4().int % 100_000_000_000:011d}"


def test_books_crud_integration_postgres() -> None:
    isbn = _unique_isbn()

    with TestClient(app) as client:
        create_resp = client.post(
            "/books",
            json={
                "title": "Clean Architecture",
                "author": "Robert C. Martin",
                "isbn": isbn,
                "total_copies": 5,
            },
        )
        assert create_resp.status_code == 201
        book = create_resp.json()
        book_id = book["id"]
        assert book["isbn"] == isbn
        assert book["total_copies"] == 5
        assert book["available_copies"] == 5

        dup_resp = client.post(
            "/books",
            json={
                "title": "Clean Architecture Duplicate",
                "author": "Robert C. Martin",
                "isbn": isbn,
                "total_copies": 2,
            },
        )
        assert dup_resp.status_code == 409

        invalid_isbn_resp = client.post(
            "/books",
            json={
                "title": "Invalid ISBN",
                "author": "Author",
                "isbn": "INVALID",
                "total_copies": 1,
            },
        )
        assert invalid_isbn_resp.status_code == 400

        invalid_copies_resp = client.post(
            "/books",
            json={
                "title": "Zero Copies",
                "author": "Author",
                "isbn": _unique_isbn(),
                "total_copies": 0,
            },
        )
        assert invalid_copies_resp.status_code == 422

        get_resp = client.get(f"/books/{book_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == book_id

        list_all_resp = client.get("/books")
        assert list_all_resp.status_code == 200
        assert any(item["id"] == book_id for item in list_all_resp.json())

        list_avail_resp = client.get("/books?available_only=true")
        assert list_avail_resp.status_code == 200
        assert any(item["id"] == book_id for item in list_avail_resp.json())

        missing_resp = client.get(f"/books/{uuid4()}")
        assert missing_resp.status_code == 404


def test_books_repository_update_filter_and_integrity_error_postgres() -> None:
    isbn = _unique_isbn()

    with TestClient(app) as client, SessionLocal() as session:
        repo = SqlAlchemyBookRepository(session)
        book = Book(
            title="Patterns of Enterprise Application Architecture",
            author="Martin Fowler",
            isbn=isbn,
            total_copies=1,
        )
        repo.save(book)
        book.allocate_copy()
        repo.save(book)

        persisted = repo.get_by_id(book.id)
        assert persisted is not None
        assert persisted.available_copies == 0

        list_all = client.get("/books").json()
        list_available = client.get("/books?available_only=true").json()
        assert any(item["id"] == str(book.id) for item in list_all)
        assert not any(item["id"] == str(book.id) for item in list_available)

        duplicate_entity = Book(
            title="Duplicate Direct Save",
            author="Martin Fowler",
            isbn=isbn,
            total_copies=1,
        )
        with pytest.raises(DuplicateIsbnError):
            repo.save(duplicate_entity)


def test_readers_crud_integration_postgres() -> None:
    suffix = uuid4().hex[:8]
    email = f"leitor.{suffix}@example.com"
    document = _unique_document()

    with TestClient(app) as client:
        create_resp = client.post(
            "/readers",
            json={
                "name": "Ricardo Vale",
                "email": email,
                "document": document,
                "category": "ACADEMIC",
            },
        )
        assert create_resp.status_code == 201
        reader = create_resp.json()
        reader_id = reader["id"]
        assert reader["email"] == email
        assert reader["document"] == document
        assert reader["category"] == "ACADEMIC"
        assert reader["active"] is True

        dup_email_resp = client.post(
            "/readers",
            json={
                "name": "Outro Leitor",
                "email": email,
                "document": _unique_document(),
            },
        )
        assert dup_email_resp.status_code == 409

        dup_doc_resp = client.post(
            "/readers",
            json={
                "name": "Terceiro Leitor",
                "email": f"outro.{suffix}@example.com",
                "document": document,
            },
        )
        assert dup_doc_resp.status_code == 409

        invalid_email_resp = client.post(
            "/readers",
            json={
                "name": "Nome Valido",
                "email": "invalid-email",
                "document": _unique_document(),
            },
        )
        assert invalid_email_resp.status_code == 400

        invalid_name_resp = client.post(
            "/readers",
            json={
                "name": "Ab",
                "email": f"ab.{suffix}@example.com",
                "document": _unique_document(),
            },
        )
        assert invalid_name_resp.status_code == 422

        get_resp = client.get(f"/readers/{reader_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == reader_id

        list_resp = client.get("/readers")
        assert list_resp.status_code == 200
        assert any(item["id"] == reader_id for item in list_resp.json())

        missing_resp = client.get(f"/readers/{uuid4()}")
        assert missing_resp.status_code == 404


def test_readers_repository_update_and_integrity_error_postgres() -> None:
    suffix = uuid4().hex[:8]
    email = f"repo.{suffix}@example.com"
    document = _unique_document()

    with TestClient(app), SessionLocal() as session:
        repo = SqlAlchemyReaderRepository(session)
        reader = Reader(
            name="Alexandre Vale",
            email=email,
            document=document,
            category=ReaderCategory.STANDARD,
        )
        repo.save(reader)
        reader.deactivate()
        repo.save(reader)

        persisted = repo.get_by_id(UUID(str(reader.id)))
        assert persisted is not None
        assert persisted.active is False

        duplicate_reader = Reader(
            name="Outro Nome",
            email=email,
            document=_unique_document(),
        )
        with pytest.raises(DuplicateReaderError):
            repo.save(duplicate_reader)
