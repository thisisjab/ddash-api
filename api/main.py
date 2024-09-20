from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.config import settings
from api.logging import configure_logging
from asgi_correlation_id import CorrelationIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)
