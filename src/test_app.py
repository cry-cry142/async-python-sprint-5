import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.db import get_session as get_db
from main import app

DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URL = (
    'postgresql+asyncpg://postgres:postgres@localhost:5432/db'
)


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    future=True
)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

app.dependency_overrides[get_db] = get_session


@pytest_asyncio.fixture
def session():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
def app():
    from main import app

    yield app


@pytest_asyncio.fixture
async def client(session, app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_api(client: AsyncClient):
    user_dict = {
        'username': 'user31',
        'password': 'password'
    }
    response = await client.post(
        '/users/',
        json=user_dict
    )
    assert response.status_code == status.HTTP_201_CREATED
    user_data = response.json()
    assert user_data['username'] == user_data['username']

    response = await client.post(
        '/users/auth',
        json=user_dict
    )
    assert response.status_code == status.HTTP_200_OK
    auth_data = response.json()
    assert auth_data['id'] == user_data['id']
    assert auth_data['username'] == user_data['username']
    assert auth_data['token'] == user_data['token']

    header_auth = {
        'Authorization': 'Bearer {}'.format(user_data['token']),
    }
    file = ('FileName3', 'Text')

    response = await client.post('/files/upload', headers=header_auth, files={
        ('path', file),
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['file_name'] == file[0]

    response = await client.get('/files/', headers=header_auth)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]['file_name'] == file[0]

    response = await client.get(
        f'/files/download?path={file[0]}',
        headers=header_auth
    )
    assert response.status_code == status.HTTP_200_OK
