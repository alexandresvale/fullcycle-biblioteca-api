from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.readers.api.dependencies import get_reader_repository
from tests.unit.readers.test_reader_use_cases import InMemoryReaderRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    repo = InMemoryReaderRepository()
    app.dependency_overrides[get_reader_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_list_and_get_reader_via_api(client: TestClient) -> None:
    create_resp = client.post(
        "/readers",
        json={
            "name": "Alexandre Vale",
            "email": "alexandre@example.com",
            "document": "123.456.789-01",
            "category": "ACADEMIC",
        },
    )
    assert create_resp.status_code == 201
    reader_data = create_resp.json()
    assert reader_data["email"] == "alexandre@example.com"
    assert reader_data["document"] == "12345678901"
    assert reader_data["category"] == "ACADEMIC"
    assert reader_data["active"] is True

    reader_id = reader_data["id"]
    get_resp = client.get(f"/readers/{reader_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Alexandre Vale"

    list_resp = client.get("/readers")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_readers_error_branches_400_404_409_422(client: TestClient) -> None:
    invalid_email = client.post(
        "/readers",
        json={
            "name": "Nome Valido",
            "email": "not-an-email",
            "document": "12345678901",
        },
    )
    assert invalid_email.status_code == 400

    short_name = client.post(
        "/readers",
        json={
            "name": "Ab",
            "email": "ab@example.com",
            "document": "12345678901",
        },
    )
    assert short_name.status_code == 422

    first = client.post(
        "/readers",
        json={
            "name": "Leitor Um",
            "email": "leitor@example.com",
            "document": "555.666.777-88",
        },
    )
    assert first.status_code == 201

    dup_email = client.post(
        "/readers",
        json={
            "name": "Leitor Dois",
            "email": "LEITOR@example.com",
            "document": "999.888.777-66",
        },
    )
    assert dup_email.status_code == 409

    dup_doc = client.post(
        "/readers",
        json={
            "name": "Leitor Tres",
            "email": "tres@example.com",
            "document": "55566677788",
        },
    )
    assert dup_doc.status_code == 409

    not_found = client.get(f"/readers/{uuid4()}")
    assert not_found.status_code == 404
