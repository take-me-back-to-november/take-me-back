from uuid import UUID

from fastapi import APIRouter, Depends, status

from dependencies.auth import get_current_user_id
from services.me.fetch_user_resume import main as fetch_user_resume
from services.me.fetch_user_status import main as fetch_user_status

router = APIRouter()


@router.get("/me/status", status_code=status.HTTP_200_OK)
async def get_user_status(
    user_id: UUID = Depends(get_current_user_id),
):
    return await fetch_user_status(user_id)


@router.get("/me/resume", status_code=status.HTTP_200_OK)
async def get_user_resume(
    user_id: UUID = Depends(get_current_user_id),
):
    return await fetch_user_resume(user_id)
