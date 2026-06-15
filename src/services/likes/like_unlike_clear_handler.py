from uuid import UUID

from fastapi import HTTPException, status

from dtos.action_dto import ActionDTO
from models.song_review import SongReview
from models.user_song_review_action import UserSongReviewAction


async def main(user_id: UUID, song_review_id: UUID, action: ActionDTO) -> None:
    review = await SongReview.filter(id=song_review_id, deleted_at=None).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    action_item = await UserSongReviewAction.filter(
        user_id=user_id,
        song_review_id=song_review_id,
        deleted_at__isnull=True,
    ).first()

    if action.action == "clear":
        if action_item:
            await action_item.soft_delete()
        return

    if not action_item:
        deleted_action_item = (
            await UserSongReviewAction.filter(
                user_id=user_id,
                song_review_id=song_review_id,
                deleted_at__isnull=False,
            )
            .order_by("-updated_at")
            .first()
        )

        if deleted_action_item:
            deleted_action_item.deleted_at = None
            deleted_action_item.action = action.action
            await deleted_action_item.save()
            return

        await UserSongReviewAction.create(
            user_id=user_id,
            song_review_id=song_review_id,
            action=action.action,
        )
        return

    action_item.action = action.action
    await action_item.save()
