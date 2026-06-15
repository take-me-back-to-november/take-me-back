from fastapi import HTTPException, status

from models.user import User


def build_user_response(user: User) -> dict:
    return {
        "id": user.id,
        "spotify_id": user.spotify_id,
        "email": user.email,
        "name": user.name,
        "picture_url": user.picture_url,
    }


async def get_user_by_id(user_id: str) -> User:
    user = await User.filter(id=user_id, deleted_at=None).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
