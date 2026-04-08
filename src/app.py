import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from sqlalchemy.exc import SQLAlchemyError

from src.config import settings
from src.controllers.exceptions import DatabaseError
from src.models.database import Base, engine
from src.models.schemas import SuccessResponse
from src.routes.auth_routes import router as auth_router
from src.routes.strategy_routes import router as strategy_router
from src.routes.user_routes import router as user_router
from src.utils.exception_handlers import register_exception_handlers
from src.utils.logging import configure_logging
from src.utils.middleware import register_middlewares
from src.utils.responses import success_response


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.validate()
    logger.info("Starting application")
    if settings.auto_create_tables:
        try:
            Base.metadata.create_all(bind=engine)
        except SQLAlchemyError as exc:
            logger.exception("Database initialization failed", exc_info=exc)
            raise DatabaseError("Unable to initialize database") from exc
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
    lifespan=lifespan,
)

register_exception_handlers(app)
register_middlewares(app)

app.include_router(auth_router)
app.include_router(strategy_router)
app.include_router(user_router)


@app.get("/", response_model=SuccessResponse[dict[str, str]])
def read_root(request: Request) -> dict:
    return success_response(
        data={"app_name": settings.app_name},
        message=f"Welcome to {settings.app_name}",
        request_id=getattr(request.state, "request_id", None),
    )


@app.get("/health", response_model=SuccessResponse[dict[str, str]])
def health_check(request: Request) -> dict:
    return success_response(
        data={"status": "ok"},
        message="Health check successful",
        request_id=getattr(request.state, "request_id", None),
    )
