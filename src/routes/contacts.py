from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contact
from src.schemas.contacts import (
    ContactSchema,
    ContactUpdateSchema,
    ContactResponse,
    ContactStatusUpdate,
)
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=list[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves a list of contacts for the authenticated user.

    :param limit: The maximum number of contacts to return. Must be between 10 and 500. Defaults to 10.
    :type limit: int
    :param offset: The number of contacts to skip before starting to collect the result set. Must be greater than or equal to 0. Defaults to 0.
    :type offset: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :return: A list of contacts.
    :rtype: list

    """
    contacts = await repository_contact.get_contacts(limit, offset, db, current_user)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves a specific contact by its ID for the authenticated user.

    :param contact_id: The ID of the contact to retrieve. Must be greater than or equal to 1.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :raises HTTPException: If the contact is not found.

    :return: The contact with the specified ID.
    :rtype: Contact
    """
    contact = await repository_contact.get_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    description="No more than 5 requests per minute",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Creates a new contact for the authenticated user.

    :param body: The data for the new contact.
    :type body: ContactSchema
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :return: The newly created contact.
    :rtype: Contact
    """
    contact = await repository_contact.create_contact(body, db, current_user)
    return contact


@router.put(
    "/{contact_id}",
    description="No more than 3 requests per minute",
    dependencies=[Depends(RateLimiter(times=3, seconds=60))],
)
async def update_contact(
    body: ContactUpdateSchema,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Updates a specific contact by its ID for the authenticated user.

    :param body: The updated data for the contact.
    :type body: ContactUpdateSchema
    :param contact_id: The ID of the contact to update. Must be greater than or equal to 1.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :raises HTTPException: If the contact is not found.

    :return: The updated contact.
    :rtype: Contact
    """
    contact = await repository_contact.update_contact(
        contact_id, body, db, current_user
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="No more than 1 request per minute",
    dependencies=[Depends(RateLimiter(times=1, seconds=60))],
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Deletes a specific contact by its ID for the authenticated user.

    :param contact_id: The ID of the contact to delete. Must be greater than or equal to 1.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :return: The deleted contact.
    :rtype: Contact
    """
    contact = await repository_contact.delete_contact(contact_id, db, current_user)
    return contact


@router.patch(
    "/{contact_id}",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    description="No more than 3 requests per minute",
    dependencies=[Depends(RateLimiter(times=3, seconds=60))],
)
async def update_status_contact(
    body: ContactStatusUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Updates the status of a specific contact by its ID for the authenticated user.

    :param body: The updated status data for the contact.
    :type body: ContactStatusUpdate
    :param contact_id: The ID of the contact to update the status.
    :type contact_id: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :raises HTTPException: If the contact is not found.

    :return: The updated contact with the new status.
    :rtype: Contact
    """
    contact = await repository_contact.update_status_contact(
        contact_id, body, db, current_user
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return contact


@router.get(
    "/search/",
    response_model=list[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def search_contacts(
    search: str = Query(min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Searches for contacts by a search query for the authenticated user.

    :param search: The search query. Must have a minimum length of 1.
    :type search: str
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :return: A list of contacts that match the search query.
    :rtype: list[Contact]

    """
    contacts = await repository_contact.search_contacts(search, db, current_user)
    return contacts


@router.get(
    "/birthdays/",
    response_model=list[ContactResponse],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_birthday_contacts(
    days: int = Query(7, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves a list of contacts with birthdays within the next specified number of days for the authenticated user.

    :param days: The number of days in the future to search for birthdays. Must be greater than or equal to 1. Defaults to 7.
    :type days: int
    :param db: The database session.
    :type db: AsyncSession
    :param current_user: The currently authenticated user.
    :type current_user: User

    :return: A list of contacts with birthdays within the specified number of days.
    :rtype: list[Contact]

    """
    contacts = await repository_contact.get_birthday_contacts(days, db, current_user)
    return contacts
