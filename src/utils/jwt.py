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


def create_spotify_state_token() -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        payload={
            "purpose": "spotify_login_state",
            "nonce": secrets.token_urlsafe(16),
            "iat": now,
            "exp": now + timedelta(minutes=10),
        },
        key=JWT_CONFIG["secret"],
        algorithm=JWT_CONFIG["algorithm"],
    )


def verify_spotify_state_token(token: str) -> bool:
    algorithm = JWT_CONFIG["algorithm"] or "HS256"
    try:
        payload = jwt.decode(
            token,
            key=JWT_CONFIG["secret"],
            algorithms=[algorithm],
        )
    except jwt.InvalidTokenError:
        return False
    return payload.get("purpose") == "spotify_login_state"


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
