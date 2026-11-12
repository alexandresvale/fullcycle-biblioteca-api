from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total de requisições HTTP processadas",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Duração das requisições HTTP em segundos",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.2, 0.5, 1.0, 2.5),
)


def metrics_endpoint() -> Response:
    """Expõe as métricas coletadas no formato de texto do Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
