from datetime import datetime, timezone

from sqlmodel import select

from app.core.repositories.base import BaseRepository
from app.db.models.refresh_token import RefreshToken


class RefreshTokenRepository(BaseRepository):
    def save(self, refresh_token: RefreshToken) -> RefreshToken:
        return self.add(refresh_token)

    def get_active_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(
            (RefreshToken.token_hash == token_hash)
            & (RefreshToken.revoked_at.is_(None))
        )
        token = self.session.exec(statement).first()
        if token and token.expires_at <= datetime.now(timezone.utc):
            return None
        return token

    def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        self.add(refresh_token)
