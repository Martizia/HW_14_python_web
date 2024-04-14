import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy import select
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
        self.contact_schema = MagicMock(spec=ContactSchema)
        self.contact_update_schema = MagicMock(spec=ContactUpdateSchema)
        self.contact_status_schema = MagicMock(spec=ContactStatusUpdate)

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

    async def test_create_contact(self):
        new_contact = {"name": "test", "lastname": "test", "email": "test", "phone": "test", "birthday": "test"}
        body = MagicMock(spec=ContactSchema)
        body.model_dump.return_value = new_contact

        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)

        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, 'test')
        self.assertEqual(result.lastname, 'test')
        self.assertEqual(result.email, 'test')
        self.assertEqual(result.phone, 'test')
        self.assertEqual(result.birthday, 'test')

    async def test_update_contact(self):
        body = ContactUpdateSchema(name='test', lastname='test', email='test@example.com', phone='123456789',
                                   birthday='2000-01-01', notes='test', favourite=False)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, name='test', lastname='test',
                                                                 email='test@example.com', phone='123456789',
                                                                 notes='test', birthday='2000-01-01', favourite=False)
        self.session.execute.return_value = mocked_contact

        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, name='test', lastname='test',
                                                                 email='test@example.com', phone='123456789',
                                                                 notes='test', birthday='2000-01-01', favourite=False)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

    async def test_update_status_contact(self):
        body = ContactStatusUpdate(name='test', lastname='test', email='test@example.com', phone='123456789',
                                   birthday='2000-01-01', notes='test', favourite=False)

        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, name='test', lastname='test',
                                                                 email='test@example.com', phone='123456789',
                                                                 notes='test', birthday='2000-01-01', favourite=False)
        self.session.execute.return_value = mocked_contact
        result = await update_status_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.favourite, body.favourite)

    async def test_search_contacts(self):
        contacts = [self.contact, self.contact]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts('test', self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_birthday_contacts(self):
        contacts = [self.contact, self.contact]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_birthday_contacts(7, self.session, self.user)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
