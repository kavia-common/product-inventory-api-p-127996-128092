import time
from collections import defaultdict, deque
from typing import Deque, Dict, Set

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


def parse_rate(rate: str) -> int:
    count, per = rate.split("/")
    n = int(count)
    seconds = 60 if per.startswith("min") else 3600 if per.startswith("hour") else 1
    return n, seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: str = "100/minute", exclude_paths: Set[str] | None = None):
        super().__init__(app)
        self.rate, self.per_seconds = parse_rate(rate_limit)
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.exclude_paths: Set[str] = exclude_paths or set()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = self.requests[ip]
        # remove old
        while window and now - window[0] > self.per_seconds:
            window.popleft()
        if len(window) >= self.rate:
            return Response("Too Many Requests", status_code=429)
        window.append(now)
        return await call_next(request)
