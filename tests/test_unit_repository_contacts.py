import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactStatusUpdate
from src.repository.contacts import create_contact, get_contact, get_contacts, update_contact, update_status_contact, \
    delete_contact, search_contacts, get_birthday_contacts


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = MagicMock()
        self.contact = MagicMock(spec=Contact)
        # self.contact_schema = MagicMock(spec=ContactSchema)
        # self.contact_update_schema = MagicMock(spec=ContactUpdateSchema)
        # self.contact_status_schema = MagicMock(spec=ContactStatusUpdate)

    async def asyncTearDown(self) -> None:
        await self.session.close()

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [self.contact, self.contact]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = self.contact
        self.session.execute.return_value = mocked_contact

        result = await get_contact(1, self.session, self.user)
        self.assertEqual(result, self.contact)


    # async def test_create_contact(self):
    #     self.contact_schema.model_dump.return_value = self.contact
    #     self.session.add.return_value = self.contact
    #     self.session.commit.return_value = None
    #     self.session.refresh.return_value = self.contact
    #     result = await create_contact(self.contact_schema, self.session, self.user)
    #     self.assertEqual(result, self.contact)

    # async def test_update_contact(self):
    #     self.contact_update_schema.model_dump.return_value = self.contact
    #     self.session.get.return_value = self.contact
    #     self.session.commit.return_value = None
    #     self.session.refresh.return_value = self.contact
    #     result = await update_contact(1, self.contact_update_schema, self.session, self.user)
    #     self.assertEqual(result, self.contact)
    #
    # async def test_update_status_contact(self):
    #     self.contact_status_schema.model_dump.return_value = self.contact
    #     self.session.get.return_value = self.contact
    #     self.session.commit.return_value = None
    #     self.session.refresh.return_value = self.contact
    #     result = await update_status_contact(1, self.contact_status_schema, self.session, self.user)
    #     self.assertEqual(result, self.contact)
    #
    # async def test_delete_contact(self):
    #     self.session.get.return_value = self.contact
    #     self.session.delete.return_value = None
    #     self.session.commit.return_value = None
    #     result = await delete_contact(1, self.session, self.user)
    #     self.assertEqual(result, None)
    #
    # async def test_search_contacts(self):
    #     self.session.execute.return_value.scalars.return_value = [self.contact]
    #     result = await search_contacts('test', self.session, self.user)
    #     self.assertEqual(result, [self.contact])
    #
    # async def test_get_birthday_contacts(self):
    #     self.session.execute.return_value.scalars.return_value = [self.contact]
    #     result = await get_birthday_contacts(self.session, self.user)
    #     self.assertEqual(result, [self.contact])


if __name__ == '__main__':
    unittest.main()
