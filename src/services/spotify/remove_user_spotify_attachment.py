from uuid import UUID

from fastapi import HTTPException, status

from models.user import User


async def main(user_id: UUID):
    user = await User.filter(id=user_id, deleted_at=None).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user.spotify_refresh_token = None
    user.spotify_access_token = None
    user.spotify_access_token_expires_at = None
    await user.save()
