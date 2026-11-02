"""
Rate Limiter ASGI / FastAPI Middleware
Chapter 4: Middleware (API Gateway) Rate Limiting

Description:
Intercepts HTTP requests, extracts client identity (client IP or API Key header),
verifies rate limits, and responds with standard HTTP 429 Too Many Requests if exceeded.
Attaches canonical headers:
- X-RateLimit-Limit
- X-RateLimit-Remaining
- X-RateLimit-Reset
- Retry-After
"""

from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from implementations.rate_limiter.base import BaseRateLimiter
from implementations.rate_limiter.token_bucket import TokenBucketRateLimiter


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware for request throttling.
    """

    def __init__(
        self,
        app,
        limiter: Optional[BaseRateLimiter] = None,
        key_func: Optional[Callable[[Request], str]] = None,
    ):
        super().__init__(app)
        self.limiter = limiter or TokenBucketRateLimiter(capacity=20, refill_rate=5.0)
        self.key_func = key_func or self._default_key_func

    @staticmethod
    def _default_key_func(request: Request) -> str:
        # Extract API key if present, otherwise fallback to client host IP
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key}"
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def dispatch(self, request: Request, call_next) -> Response:
        # Exempt health check and docs
        path = request.url.path
        if path.startswith(("/docs", "/openapi.json", "/health", "/favicon.ico", "/static")):
            return await call_next(request)

        key = self.key_func(request)
        result = self.limiter.allow_request(key)

        if not result.allowed:
            headers = {
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(round(result.reset_after, 2)),
                "Retry-After": str(int(result.retry_after or 1)),
            }
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit quota exceeded. Please slow down.",
                    "retry_after_seconds": result.retry_after,
                },
                headers=headers,
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(round(result.reset_after, 2))
        return response

