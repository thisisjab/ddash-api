from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from api.config import settings
from api.logging import configure_logging
from api.projects.routes import router as projects_router
from api.users.routes import router as users_router


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
    root_path="/api/v1",
)
app.add_middleware(CorrelationIdMiddleware)


app.include_router(users_router)
app.include_router(projects_router)
