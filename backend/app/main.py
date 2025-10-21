from contextlib import asynccontextmanager
from fastapi import (FastAPI,
                     Request)
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import get_settings
from app.core.logging import (setup_logging,
                              get_logger)
from app.core.rate_limit import limiter
from app.database import (init_connection_pool,
                          test_connection,
                          close_connection_pool,
                          init_db)
from app.routes import api_router
from app.middleware.request_id import RequestIDMiddleware


setup_logging(level="INFO", json_format=False)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    logger.info("Starting application...")
    try:
        pool = init_connection_pool()
        if pool is not None:
            if test_connection():
                logger.info("Database connection pool established successfully")
            else:
                logger.error("Database connection test failed")
                raise ConnectionError("Failed to connect to database")
        else:
            logger.error("Database connection pool initialization failed")
            raise ConnectionError("Failed to initialize database connection pool")

        logger.info("Initializing database schema...")
        init_db()
        logger.info("Database schema initialized successfully")

    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        raise

    yield

    logger.info("Shutting down application...")
    try:
        close_connection_pool()
        logger.info("Database connection pool closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Request ID middleware (should be first to track all requests)
    app.add_middleware(RequestIDMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    app.include_router(api_router)

    return app


app = create_application()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host='0.0.0.0',
        port=5000,
        reload=True
    )
