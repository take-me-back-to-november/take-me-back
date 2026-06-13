import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pydantic import BaseModel

from config.jwt import JWT_CONFIG


class JwtPayload(BaseModel):
    sub: str
    iat: datetime
    exp: datetime


def build_access_jwt_token_payload(user_id: UUID) -> dict[str, datetime | str]:
    expires_minutes = int(JWT_CONFIG["expires_minutes"] or 30)
    now = datetime.now(UTC)
    return {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }


def create_access_jwt_token(user_id: UUID) -> str:
    return jwt.encode(
        payload=build_access_jwt_token_payload(user_id),
        key=JWT_CONFIG["secret"],
        algorithm=JWT_CONFIG["algorithm"],
    )


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def decode_jwt_token(token: str) -> JwtPayload:
    algorithm = JWT_CONFIG["algorithm"] or "HS256"
    decoded_payload = jwt.decode(
        token,
        key=JWT_CONFIG["secret"],
        algorithms=[algorithm],
    )
    return JwtPayload(
        sub=decoded_payload["sub"],
        iat=decoded_payload["iat"],
        exp=decoded_payload["exp"],
    )
