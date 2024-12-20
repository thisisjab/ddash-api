from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.logging import configure_logging
from api.orgs.routes import router as orgs_router
from api.projects.routes import router as projects_router
from api.tasks.routes import router as tasks_router
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
)
app.add_middleware(CorrelationIdMiddleware)


app.include_router(users_router)
app.include_router(orgs_router)
app.include_router(projects_router)
app.include_router(tasks_router)
