import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add a unique request ID to each request.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and add request ID.
        """
        request_id = request.headers.get("X-Request-ID")

        if not request_id:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id

            logger.info(
                f"Outgoing response: {response.status_code}",
                extra={"request_id": request_id}
            )

            return response
        except Exception as e:
            logger.error(
                f"Request failed: {str(e)}",
                extra={"request_id": request_id},
                exc_info=True
            )
            raise
