from fastapi import HTTPException, status

from models.user import User
from utils.jwt import create_access_jwt_token


async def main(refresh_token: str) -> dict:
    user = await User.filter(refresh_token=refresh_token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return {
        "access_token": create_access_jwt_token(user_id=user.id),
    }
