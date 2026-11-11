from uuid import uuid4

from fastapi.testclient import TestClient

from src.main import app


def test_full_loan_and_return_flow_integration() -> None:
    book_id = str(uuid4())
    reader_id = str(uuid4())

    with TestClient(app) as client:
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

        conflict_resp = client.post(
            "/loans",
            json={
                "book_id": book_id,
                "reader_id": str(uuid4()),
                "borrowed_at": "2026-11-02",
                "due_date": "2026-11-09",
            },
        )
        assert conflict_resp.status_code == 409

        return_resp = client.post(
            f"/loans/{loan_id}/return",
            json={"returned_at": "2026-11-08", "policy_type": "STANDARD"},
        )
        assert return_resp.status_code == 200
        returned_data = return_resp.json()
        assert returned_data["status"] == "RETURNED"
        assert returned_data["fine_amount"] == "6.00"

        get_resp = client.get(f"/loans/{loan_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "RETURNED"

        list_resp = client.get("/loans")
        assert list_resp.status_code == 200
        assert any(item["id"] == loan_id for item in list_resp.json())
