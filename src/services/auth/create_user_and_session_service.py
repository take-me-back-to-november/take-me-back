from fastapi import HTTPException

from dtos.user_dtos import CreateUserAndSessionDTO
from models.user import User
from utils.auth import get_account_changes, get_user_info
from utils.jwt import create_access_jwt_token, create_refresh_token
from utils.users import build_user_response


async def main(body: CreateUserAndSessionDTO) -> dict:
    user_info = await get_user_info(body.google_id)
    google_sub = user_info.sub

    if not google_sub:
        raise HTTPException(401, "Invalid Google ID token")

    user = await User.filter(google_id=google_sub).first()

    if not user:
        user = await User.create(
            google_id=google_sub,
            google_email=user_info.email,
            name=user_info.name,
            first_name=user_info.given_name,
            last_name=user_info.family_name,
            picture_url=user_info.picture,
            hosted_domain=user_info.hd,
            email_verified=user_info.email_verified,
            refresh_token=create_refresh_token(),
        )

    account_changes = get_account_changes(user, user_info)

    if user and account_changes:
        await user.update_from_dict(account_changes)

    return {
        "user": build_user_response(user),
        "access_token": create_access_jwt_token(user_id=user.id),
        "refresh_token": user.refresh_token,
    }
