"""
=========================================================
Request Timing & Logging Middleware
ECG Clinical Decision Support System
=========================================================
Logs incoming HTTP request processing duration and injects
X-Process-Time header into response headers.
=========================================================
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config.logging_config import setup_logger

logger = setup_logger("request_timing")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request execution duration and attach X-Process-Time header.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"Unhandled exception during {request.method} {request.url.path} "
                f"after {process_time:.4f}s: {exc}"
            )
            raise exc

        process_time = time.perf_counter() - start_time
        process_time_str = f"{process_time:.4f}s"
        
        response.headers["X-Process-Time"] = process_time_str

        # Skip logging health checks to avoid noise
        if request.url.path not in ["/health", "/"]:
            logger.info(
                f"{request.method} {request.url.path} -> Status {response.status_code} "
                f"[{process_time_str}]"
            )

        return response
