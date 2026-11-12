import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.observability.logger import get_logger
from src.core.observability.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)

logger = get_logger()


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware para injeção de X-Request-ID, métricas Prometheus e logs JSON."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start_time
            duration_ms = round(duration * 1000, 2)
            endpoint = request.url.path

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method, endpoint=endpoint, status=500
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method, endpoint=endpoint
            ).observe(duration)

            logger.error(
                "http_request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
                error=str(exc),
            )
            raise exc

        duration = time.perf_counter() - start_time
        duration_ms = round(duration * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        route = request.scope.get("route")
        endpoint = route.path if route and hasattr(route, "path") else request.url.path

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method, endpoint=endpoint, status=response.status_code
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method, endpoint=endpoint
        ).observe(duration)

        if request.url.path != "/health":
            logger.info(
                "http_request_finished",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                endpoint=endpoint,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        return response
