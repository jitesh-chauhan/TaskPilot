import asyncio
import os
import sys
import time
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient

from core.config import settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.database.database import get_db
    from app.main import app

except ImportError as e:
    print(f"Import error: {e}")
    from fastapi import FastAPI

    app = FastAPI()
    get_db = None


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def mock_mongo_client():
    mock_client = Mock(spec=AsyncMongoClient)
    mock_db = Mock()
    mock_collection = Mock()

    mock_collection.find_one = AsyncMock()
    mock_collection.insert_one = AsyncMock()
    mock_collection.update_one = AsyncMock()
    mock_collection.delete_one = AsyncMock()
    mock_collection.find = AsyncMock()
    mock_collection.count_documents = AsyncMock()
    mock_db.__getitem__ = Mock(return_value=mock_collection)
    mock_db.users = mock_collection
    mock_client.get_database = Mock(return_value=mock_db)

    return mock_client


@pytest.fixture(scope="function")
async def mock_db(mock_mongo_client):
    db = mock_mongo_client.get_database()
    return db


@pytest.fixture(scope="function")
def mock_get_db(mock_db):
    async def override_get_db():
        yield mock_db

    return override_get_db


@pytest.fixture(scope="function", autouse=True)
async def set_test_db(mock_db):
    app.state.db = mock_db
    yield
    app.state.db = None


@pytest.fixture(scope="function")
async def client_with_mock_db(async_client, mock_get_db):

    if get_db is not None:
        app.dependency_overrides[get_db] = mock_get_db

    yield async_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "password": "securepassword123",
        "username": "Test User",
    }


@pytest.fixture
def sample_user_document():
    return {
        "_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "username": "Test User",
        "role": "user",
        "enabled": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_todo_data():
    return {
        "title": "Test Todo Item",
        "description": "This is a test todo description",
        "priority": 3,
        "due_date": str(int(datetime.now().timestamp() * 1000) + 86400000),
        "completed": False,
    }


@pytest.fixture
def sample_todo_document():
    return {
        "_id": "507f1f77bcf86cd799439012",
        "user_id": "507f1f77bcf86cd799439011",
        "title": "Test Todo Item",
        "description": "This is a test todo description",
        "priority": 3,
        "due_date": str(int(datetime.now().timestamp() * 1000) + 86400000),
        "completed": False,
        "is_deleted": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "deleted_at": None,
    }


@pytest.fixture
def sample_todo_list():
    now_ms = str(int(time.time() * 1000))

    return [
        {
            "_id": "507f1f77bcf86cd799439012",
            "user_id": "test@example.com",
            "title": "Todo 1",
            "description": "First todo",
            "due_date": now_ms,
            "completed": False,
            "priority": "High",
            "created_at": now_ms,
            "updated_at": "",
            "is_deleted": False,
            "deleted_at": "",
        },
        {
            "_id": "507f1f77bcf86cd799439013",
            "user_id": "test@example.com",
            "title": "Todo 2",
            "description": "Second todo",
            "due_date": now_ms,
            "completed": True,
            "priority": "Low",
            "created_at": now_ms,
            "updated_at": "",
            "is_deleted": False,
            "deleted_at": "",
        },
    ]


@pytest.fixture
def auth_token():
    try:
        from app.utils.auth_utils import signJWT

        return signJWT("507f1f77bcf86cd799439011")["access_token"]

    except Exception:
        return (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZX"
            "N0QGV4YW1wbGUuY29tIiwid"
            "XNlcl9pZCI6IjUwN2YxZjc3YmNmODZjZDc5OTQzOT"
            "AxMSJ9.test_signature"
        )


@pytest.fixture
def auth_headers(auth_token):
    return {settings.JWT_SECRET_KEY: f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture
def authenticated_client(async_client, auth_headers):
    async_client.headers.update(auth_headers)
    return async_client


@pytest.fixture
def mock_password_hash():
    with patch(
        "app.apis.auth.views.verify_password",
        return_value=True,
    ):
        yield


@pytest.fixture
def mock_jwt():
    with patch(
        "app.utils.auth_utils.signJWT",
        return_value={"access_token": "mocked_token"},
    ):
        yield
