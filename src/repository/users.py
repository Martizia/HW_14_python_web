from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.database.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a user by their email.

    :param email: User's email.
    :type email: str
    :param db: Asynchronous session object of the database.
    :type db: AsyncSession
    :return: User object from the database.
    :rtype: User
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Creates a new user.

    :param body: User data
    :type body: UserSchema
    :param db: Asynchronous session object of the database.
    :type db: AsyncSession
    :return: Created user object.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Updates a user's token.

    :param user: User object.
    :type user: User
    :param token: New user token.
    :type token: str | None
    :param db: Asynchronous session object of the database.
    :type db: AsyncSession
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirms a user's email.

    :param email: User's email.
    :type email: str
    :param db: Asynchronous session object of the database.
    :type db: AsyncSession
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession):
    """
    Updates a user's avatar URL.

    :param email: User's email.
    :type email: str
    :param url: New user avatar URL.
    :type url: str | None
    :param db: Asynchronous session object of the database.
    :type db: AsyncSession
    :return: Updated user object.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
