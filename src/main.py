from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response

from src.core.config import settings
from src.core.database import Base, engine
from src.core.observability.logger import setup_logging
from src.core.observability.metrics import metrics_endpoint
from src.core.observability.middleware import ObservabilityMiddleware
from src.modules.books.api.router import router as books_router
from src.modules.books.data.model import BookModel  # noqa: F401
from src.modules.loans.api.loans_router import router as loans_router
from src.modules.loans.data.loan_model import LoanModel  # noqa: F401
from src.modules.readers.api.router import router as readers_router
from src.modules.readers.data.model import ReaderModel  # noqa: F401

setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
)

app.add_middleware(ObservabilityMiddleware)

app.include_router(books_router)
app.include_router(readers_router)
app.include_router(loans_router)


@app.get("/health", tags=["Health"], summary="Health check da aplicação")
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.get("/metrics", tags=["Observability"], summary="Métricas no formato Prometheus")
def get_metrics() -> Response:
    return metrics_endpoint()
