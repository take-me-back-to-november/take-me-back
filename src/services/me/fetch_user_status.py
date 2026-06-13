from uuid import UUID

from fastapi import HTTPException, status

from models.user import User


async def main(user_id: UUID) -> dict:
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "spotify_connected": bool(user.spotify_refresh_token),
    }
