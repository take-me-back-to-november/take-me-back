from uuid import UUID

from fastapi import APIRouter, Depends, status

from dependencies.auth import get_current_user_id
from dtos.action_dto import ActionDTO
from services.likes.like_unlike_clear_handler import (
    main as like_unlike_clear_handler,
)

router = APIRouter(prefix="/reviews")


@router.post("/{review_id}/actions", status_code=status.HTTP_204_NO_CONTENT)
async def set_song_review_action(
    review_id: UUID,
    body: ActionDTO,
    user_id: UUID = Depends(get_current_user_id),
):
    await like_unlike_clear_handler(user_id, review_id, body)
