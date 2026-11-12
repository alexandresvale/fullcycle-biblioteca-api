from fastapi import APIRouter
from fastapi.testclient import TestClient

from src.main import app

dummy_router = APIRouter()


@dummy_router.get("/test-error-endpoint")
def trigger_error() -> None:
    raise RuntimeError("Erro simulado para teste de observabilidade")


app.include_router(dummy_router)


def test_health_check_returns_ok_with_request_id() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "development"}
    assert "X-Request-ID" in response.headers


def test_custom_request_id_is_propagated() -> None:
    client = TestClient(app)
    custom_id = "test-custom-request-id-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


def test_metrics_endpoint_returns_prometheus_format() -> None:
    client = TestClient(app)
    # Trigger at least one request to populate metrics
    client.get("/health")

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body


def test_middleware_handles_unhandled_exception() -> None:
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test-error-endpoint")
    assert response.status_code == 500
