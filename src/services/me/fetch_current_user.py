from uuid import UUID

from utils.users import build_user_response, get_user_by_id


async def main(user_id: UUID):
    user = await get_user_by_id(str(user_id))
    return build_user_response(user)
