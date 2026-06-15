from fastapi import HTTPException, status

from models.user import User


def build_user_response(user: User) -> dict:
    return {
        "id": user.id,
        "google_id": user.google_id,
        "google_email": user.google_email,
        "email_verified": user.email_verified,
        "name": user.name,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture_url": user.picture_url,
        "hosted_domain": user.hosted_domain,
    }


async def get_user_by_id(user_id: str) -> User:
    user = await User.filter(id=user_id, deleted_at=None).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
