from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.loans.api.dependencies import get_loan_repository
from tests.unit.loans.test_loan_use_cases import InMemoryLoanRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    repo = InMemoryLoanRepository()
    app.dependency_overrides[get_loan_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_list_get_and_return_loan_via_api(client: TestClient) -> None:
    book_id = str(uuid4())
    reader_id = str(uuid4())

    create_resp = client.post(
        "/loans",
        json={
            "book_id": book_id,
            "reader_id": reader_id,
            "borrowed_at": "2026-11-01",
            "due_date": "2026-11-05",
        },
    )
    assert create_resp.status_code == 201
    loan_data = create_resp.json()
    loan_id = loan_data["id"]
    assert loan_data["status"] == "ACTIVE"

    get_resp = client.get(f"/loans/{loan_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == loan_id

    list_resp = client.get("/loans")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    return_resp = client.post(
        f"/loans/{loan_id}/return",
        json={"returned_at": "2026-11-09", "policy_type": "ACADEMIC"},
    )
    assert return_resp.status_code == 200
    returned_data = return_resp.json()
    assert returned_data["status"] == "RETURNED"
    assert returned_data["fine_amount"] == "3.00"


def test_create_loan_conflict_and_limit_errors(client: TestClient) -> None:
    book_id = str(uuid4())
    reader_id = str(uuid4())

    first = client.post(
        "/loans",
        json={
            "book_id": book_id,
            "reader_id": reader_id,
            "borrowed_at": "2026-11-01",
            "due_date": "2026-11-05",
        },
    )
    assert first.status_code == 201

    duplicate_book = client.post(
        "/loans",
        json={
            "book_id": book_id,
            "reader_id": str(uuid4()),
            "borrowed_at": "2026-11-01",
            "due_date": "2026-11-05",
        },
    )
    assert duplicate_book.status_code == 409

    for _ in range(2):
        resp = client.post(
            "/loans",
            json={
                "book_id": str(uuid4()),
                "reader_id": reader_id,
                "borrowed_at": "2026-11-01",
                "due_date": "2026-11-05",
            },
        )
        assert resp.status_code == 201

    fourth_loan = client.post(
        "/loans",
        json={
            "book_id": str(uuid4()),
            "reader_id": reader_id,
            "borrowed_at": "2026-11-01",
            "due_date": "2026-11-05",
        },
    )
    assert fourth_loan.status_code == 422


def test_loan_error_branches_400_404_409(client: TestClient) -> None:
    invalid_dates = client.post(
        "/loans",
        json={
            "book_id": str(uuid4()),
            "reader_id": str(uuid4()),
            "borrowed_at": "2026-11-10",
            "due_date": "2026-11-05",
        },
    )
    assert invalid_dates.status_code == 400

    missing_id = str(uuid4())
    assert client.get(f"/loans/{missing_id}").status_code == 404
    assert (
        client.post(f"/loans/{missing_id}/return", json={"returned_at": "2026-11-08"}).status_code
        == 404
    )

    valid_loan = client.post(
        "/loans",
        json={
            "book_id": str(uuid4()),
            "reader_id": str(uuid4()),
            "borrowed_at": "2026-11-05",
            "due_date": "2026-11-10",
        },
    ).json()
    loan_id = valid_loan["id"]

    invalid_return_date = client.post(
        f"/loans/{loan_id}/return",
        json={"returned_at": "2026-11-01", "policy_type": "STANDARD"},
    )
    assert invalid_return_date.status_code == 400

    first_return = client.post(
        f"/loans/{loan_id}/return",
        json={"returned_at": "2026-11-10", "policy_type": "STANDARD"},
    )
    assert first_return.status_code == 200

    second_return = client.post(
        f"/loans/{loan_id}/return",
        json={"returned_at": "2026-11-11", "policy_type": "STANDARD"},
    )
    assert second_return.status_code == 409

