from datetime import datetime, timedelta

from sqlalchemy import select, or_, extract, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactStatusUpdate


async def get_contacts(limit: int, offset: int, db: AsyncSession, current_user: User):
    stmt = select(Contact).filter_by(user=current_user).offset(offset).limit(limit)
    contact = await db.execute(stmt)
    return contact.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, current_user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, current_user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=current_user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, current_user: User
):
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
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.favourite = body.favourite
        await db.commit()
        await db.refresh(contact)
    return contact


async def search_contacts(search: str, db: AsyncSession, current_user: User):
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
