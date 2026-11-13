from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.books.api.dependencies import get_book_repository
from tests.unit.books.test_book_use_cases import InMemoryBookRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    repo = InMemoryBookRepository()
    app.dependency_overrides[get_book_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_list_and_get_book_via_api(client: TestClient) -> None:
    create_resp = client.post(
        "/books",
        json={
            "title": "Clean Architecture",
            "author": "Robert C. Martin",
            "isbn": "978-0-13-449416-6",
            "total_copies": 3,
        },
    )
    assert create_resp.status_code == 201
    book_data = create_resp.json()
    assert book_data["isbn"] == "9780134494166"
    assert book_data["available_copies"] == 3

    book_id = book_data["id"]
    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Clean Architecture"

    list_resp = client.get("/books?available_only=true")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_books_error_branches_400_404_409_422(client: TestClient) -> None:
    invalid_isbn = client.post(
        "/books",
        json={
            "title": "Invalid ISBN",
            "author": "Author",
            "isbn": "INVALID",
            "total_copies": 1,
        },
    )
    assert invalid_isbn.status_code == 400

    invalid_copies = client.post(
        "/books",
        json={
            "title": "Zero Copies",
            "author": "Author",
            "isbn": "9780134494166",
            "total_copies": 0,
        },
    )
    assert invalid_copies.status_code == 422

    first = client.post(
        "/books",
        json={
            "title": "DDD",
            "author": "Eric Evans",
            "isbn": "9780321125217",
            "total_copies": 2,
        },
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/books",
        json={
            "title": "DDD Duplicate",
            "author": "Eric Evans",
            "isbn": "978-0-321-12521-7",
            "total_copies": 1,
        },
    )
    assert duplicate.status_code == 409

    not_found = client.get(f"/books/{uuid4()}")
    assert not_found.status_code == 404
