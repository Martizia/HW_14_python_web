from datetime import datetime, timedelta

from sqlalchemy import select, or_, extract, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactStatusUpdate


async def get_contacts(limit: int, offset: int, db: AsyncSession, current_user: User):
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param limit: The number of contacts to skip.
    :type limit: int
    :param offset: The maximum number of contacts to return.
    :type offset: int
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to retrieve contacts for.
    :type current_user: User
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    stmt = select(Contact).filter_by(user=current_user).offset(offset).limit(limit)
    contact = await db.execute(stmt)
    return contact.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to retrieve the contact for.
    :type current_user: User
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Contact | None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, current_user: User):
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactSchema
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to create the contact for.
    :type current_user: User
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=current_user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
        contact_id: int, body: ContactUpdateSchema, db: AsyncSession, current_user: User):
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactUpdateSchema
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to update the contact for.
    :type current_user: User
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.notes = body.notes
        contact.favourite = body.favourite
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to remove the contact for.
    :type current_user: User
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def update_status_contact(
        contact_id: int, body: ContactStatusUpdate, db: AsyncSession, current_user: User
):
    """
    Updates the status (i.e. "favourite" or "not favourite") of a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated status for the contact.
    :type body: ContactStatusUpdate
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to update the contact for.
    :type current_user: User
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.favourite = body.favourite
        await db.commit()
        await db.refresh(contact)
    return contact


async def search_contacts(search: str, db: AsyncSession, current_user: User):
    """
    Searches of a contact by fields 'name', 'lastname' or 'email' for a specific user.

    :param search: The field with information for search the contact.
    :type search: str
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to search the contact for.
    :type current_user: User
    :return: The contact that matches the search, or None if it does not exist.
    :rtype: Contact | None
    """
    stmt = (
        select(Contact)
        .filter_by(user=current_user)
        .where(
            or_(
                Contact.name.ilike(f"%{search}%"),
                Contact.lastname.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_birthday_contacts(days: int, db: AsyncSession, current_user: User):
    """
    Returns a list of contact(-s) who has birthday within specified range of days for a specific user.

    :param days: The number of days that define the range.
    :type days: int
    :param db: The async database session.
    :type db: AsyncSession
    :param current_user: The user to show the contact(-s) for.
    :type current_user: User
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    birthday_month = extract("month", Contact.birthday)
    birthday_day = extract("day", Contact.birthday)

    current_year_birthday = func.to_date(
        func.concat(
            func.to_char(today, "YYYY"),
            "-",
            func.to_char(birthday_month, "FM00"),
            "-",
            func.to_char(birthday_day, "FM00"),
        ),
        "YYYY-MM-DD",
    )

    next_year_birthday = func.to_date(
        func.concat(
            func.to_char(today + timedelta(days=365), "YYYY"),
            "-",
            func.to_char(birthday_month, "FM00"),
            "-",
            func.to_char(birthday_day, "FM00"),
        ),
        "YYYY-MM-DD",
    )

    stmt = (
        select(Contact)
        .filter_by(user=current_user)
        .where(
            or_(
                current_year_birthday.between(today, end_date),
                next_year_birthday.between(today, end_date),
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()
