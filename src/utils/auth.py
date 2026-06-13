from fastapi import HTTPException, status

from config.oauth import GOOGLE_OAUTH_CONFIG
from dtos.user_dtos import GoogleUserInfoDTO
from instances.http_client import get_http_client
from models.user import User


def parse_email_verified(value: str | bool | None) -> bool | None:
    if value is None:
        return None
    if value in (True, "true"):
        return True
    if value in (False, "false"):
        return False
    return None


def get_account_changes(
    user: User, user_info: GoogleUserInfoDTO
) -> dict[str, str | bool | None] | None:
    changes: dict[str, str | bool | None] = {}
    if user.google_email != user_info.email:
        changes["google_email"] = user_info.email
    if user.name != user_info.name:
        changes["name"] = user_info.name
    if user.first_name != user_info.given_name:
        changes["first_name"] = user_info.given_name
    if user.last_name != user_info.family_name:
        changes["last_name"] = user_info.family_name
    if user.picture_url != user_info.picture:
        changes["picture_url"] = user_info.picture
    if user.hosted_domain != user_info.hd:
        changes["hosted_domain"] = user_info.hd
    if user.email_verified != user_info.email_verified:
        changes["email_verified"] = user_info.email_verified
    return changes or None


async def get_user_info(id_token: str) -> GoogleUserInfoDTO:
    base_url = GOOGLE_OAUTH_CONFIG["base_url"]
    client = get_http_client()
    response = await client.get(
        f"{base_url}/tokeninfo",
        params={"id_token": id_token},
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )
    data = response.json()
    return GoogleUserInfoDTO(
        sub=data.get("sub"),
        email=data.get("email"),
        name=data.get("name"),
        given_name=data.get("given_name"),
        family_name=data.get("family_name"),
        picture=data.get("picture"),
        hd=data.get("hd"),
        email_verified=parse_email_verified(data.get("email_verified")),
    )
