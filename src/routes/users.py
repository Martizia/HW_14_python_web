import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.database.config import config
from src.repository import users as repository_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/myself",
    response_model=UserResponse,
    description="No more than 2 requests per 20 seconds",
    dependencies=[Depends(RateLimiter(times=2, seconds=20))],
)
async def get_current_user(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    description="No more than 1 requests per minute",
    dependencies=[Depends(RateLimiter(times=1, seconds=60))],
)
async def change_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    public_id = f"HW-13/{current_user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repository_users.update_avatar_url(current_user.email, res_url, db)
    return user
