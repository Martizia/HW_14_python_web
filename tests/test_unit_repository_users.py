import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema, ContactStatusUpdate
from src.schemas.user import UserSchema
from src.repository.users import create_user, get_user_by_email, update_avatar_url, update_token, confirmed_email


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = MagicMock()
        self.contact = MagicMock(spec=Contact)
        self.contact_schema = MagicMock(spec=ContactSchema)
        self.contact_update_schema = MagicMock(spec=ContactUpdateSchema)
        self.contact_status_schema = MagicMock(spec=ContactStatusUpdate)

    async def asyncTearDown(self) -> None:
        await self.session.close()

    async def test_get_user_by_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email('test@example.com', self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self):
        body = UserSchema(username='test', email='test@example.com', password='12345678')
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_user

        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)

    async def test_update_token(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await update_token(self.user, 'test', self.session)
        self.assertEqual(result, None)

    async def test_confirmed_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await confirmed_email('test@example.com', self.session)
        self.assertEqual(result, None)

    async def test_update_avatar_url(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user
        result = await update_avatar_url('test@example.com', 'test', self.session)
        self.assertEqual(result, self.user)


if __name__ == '__main__':
    unittest.main()
