import pytest
import pytest_asyncio
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from database import init_db, UserDB, ListingDB, AlertDB

@pytest_asyncio.fixture
async def db():
    """Temporary file database for each test (auto‑deleted)."""
    import database
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database.DB_PATH = path
    await init_db()
    yield
    # Cleanup
    os.unlink(path)

@pytest.fixture
def mock_message():
    msg = AsyncMock()
    msg.from_user.id = 123
    msg.text = ""
    msg.answer = AsyncMock()
    return msg

@pytest.fixture
def mock_callback():
    cb = AsyncMock()
    cb.from_user.id = 123
    cb.data = ""
    cb.message = AsyncMock()
    cb.answer = AsyncMock()
    return cb

@pytest.fixture
def translations():
    return {
        "no_role": "Please /start",
        "role_selected_realtor": "You are a realtor",
        "role_selected_client": "You are a client",
        "role_realtor": "Риелтор",
        "role_client": "Клиент",
        "greeting": "Welcome",
        "stats_header": "Stats: {users} users, {listings} listings",
        "welcome_title": "Welcome",
        "welcome_subtitle": "Subtitle"
    }