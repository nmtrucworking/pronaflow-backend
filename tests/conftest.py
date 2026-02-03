"""
Pytest configuration and fixtures for PronaFlow backend tests.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.db.declarative_base import Base
from app.db.session import get_db
from app.core.config import settings


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def engine():
    """Create a test database engine with in-memory SQLite."""
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for async endpoint tests."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# Sample data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "SecurePassword123!",
        "is_active": True,
        "is_verified": False
    }


@pytest.fixture
def sample_workspace_data():
    """Sample workspace data for testing."""
    return {
        "name": "Test Workspace",
        "slug": "test-workspace",
        "description": "A test workspace",
        "is_active": True
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "key": "TEST",
        "description": "A test project",
        "status": "NOT_STARTED",
        "governance_mode": "SIMPLE"
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "A test task",
        "status": "TODO",
        "priority": "MEDIUM"
    }
