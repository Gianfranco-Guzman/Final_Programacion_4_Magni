from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.config import get_settings


class AuthRateLimiter:
    def __init__(self) -> None:
        self._failures: dict[tuple[str, str], deque[datetime]] = defaultdict(deque)

    def ensure_allowed(self, scope: str, identifier: str) -> None:
        settings = get_settings()
        now = datetime.now(timezone.utc)
        window = timedelta(minutes=settings.auth_rate_limit_window_minutes)
        key = (scope, identifier)
        entries = self._failures[key]
        while entries and now - entries[0] > window:
            entries.popleft()

        if len(entries) >= settings.auth_rate_limit_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos fallidos. Reintentá más tarde.",
                headers={"Retry-After": str(settings.auth_rate_limit_window_minutes * 60)},
            )

    def register_failure(self, scope: str, identifier: str) -> None:
        key = (scope, identifier)
        self._failures[key].append(datetime.now(timezone.utc))

    def clear(self, scope: str, identifier: str) -> None:
        self._failures.pop((scope, identifier), None)


auth_rate_limiter = AuthRateLimiter()
