from unittest.mock import Mock

import pytest
from sqlalchemy import select
from src.database.models import User
from tests.conftest import TestingSessionLocal
from src.database import messages

user_data = {"username": "test", "email": "test@example.com", "password": "12345678"}
user_data2 = {"username": "test2", "email": "test2@example.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data2)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data2["username"]
    assert data["email"] == user_data2["email"]
    assert "password" not in data
    assert "avatar" in data


def test_signup_existing_user(client):
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_wrong_email_login(client):
    response = client.post("api/auth/login",
                           data={"username": "email", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL


@pytest.mark.asyncio
async def test_email_not_confirmed_during_login(client):
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == user_data.get("email")))
        user = result.scalar_one_or_none()
        if user:
            user.confirmed = False
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.EMAIL_NOT_CONFIRMED

    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == user_data.get("email")))
        user = result.scalar_one_or_none()
        if user:
            user.confirmed = True
            await session.commit()


def test_invalid_password_during_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data



