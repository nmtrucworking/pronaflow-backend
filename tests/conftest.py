"""
Pytest Configuration and Fixtures for PronaFlow Tests
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid
from datetime import datetime

from app.main import app
from app.db.declarative_base import Base
from app.db.session import get_db
from app.db.models.users import User
from app.db.models.workspaces import Workspace, WorkspaceMember
from app.db.models.projects import Project
from app.db.models.tasks import Task, TaskList, TaskAssignee
from app.db.enums import UserStatus, WorkspaceRole, ProjectStatus, TaskStatus, TaskPriority
from app.utils.helpers import hash_password


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
def db(engine) -> Generator[Session, None, None]:
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
def client(db) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for async endpoint tests."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ==================== USER FIXTURES ====================

@pytest.fixture
def test_user(db: Session) -> User:
    """Create test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash=hash_password("Password123!"),
        full_name="Test User",
        status=UserStatus.ACTIVE,
        email_verified_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create admin test user."""
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        username="adminuser",
        password_hash=hash_password("AdminPass123!"),
        full_name="Admin User",
        status=UserStatus.ACTIVE,
        email_verified_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def another_user(db: Session) -> User:
    """Create another test user."""
    user = User(
        id=uuid.uuid4(),
        email="other@example.com",
        username="otheruser",
        password_hash=hash_password("Other123!"),
        full_name="Other User",
        status=UserStatus.ACTIVE,
        email_verified_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==================== WORKSPACE FIXTURES ====================

@pytest.fixture
def test_workspace(db: Session, test_user) -> Workspace:
    """Create test workspace."""
    workspace = Workspace(
        id=uuid.uuid4(),
        name="Test Workspace",
        description="A test workspace",
        owner_id=test_user.id,
        status="ACTIVE",
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@pytest.fixture
def test_workspace_member(db: Session, test_workspace, another_user) -> WorkspaceMember:
    """Add member to test workspace."""
    member = WorkspaceMember(
        id=uuid.uuid4(),
        workspace_id=test_workspace.id,
        user_id=another_user.id,
        role=WorkspaceRole.MEMBER,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


# ==================== PROJECT FIXTURES ====================

@pytest.fixture
def test_project(db: Session, test_workspace, test_user) -> Project:
    """Create test project."""
    project = Project(
        id=uuid.uuid4(),
        workspace_id=test_workspace.id,
        owner_id=test_user.id,
        name="Test Project",
        description="A test project",
        status=ProjectStatus.NOT_STARTED,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ==================== TASK FIXTURES ====================

@pytest.fixture
def test_task_list(db: Session, test_project) -> TaskList:
    """Create test task list."""
    task_list = TaskList(
        id=uuid.uuid4(),
        project_id=test_project.id,
        name="Test List",
        order=0,
    )
    db.add(task_list)
    db.commit()
    db.refresh(task_list)
    return task_list


@pytest.fixture
def test_task(db: Session, test_project, test_task_list, test_user) -> Task:
    """Create test task."""
    task = Task(
        id=uuid.uuid4(),
        project_id=test_project.id,
        task_list_id=test_task_list.id,
        title="Test Task",
        description="A test task",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_by=test_user.id,
        order=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def test_task_assignee(db: Session, test_task, test_user) -> TaskAssignee:
    """Assign test task to user."""
    assignee = TaskAssignee(
        id=uuid.uuid4(),
        task_id=test_task.id,
        user_id=test_user.id,
        is_primary=True,
    )
    db.add(assignee)
    db.commit()
    db.refresh(assignee)
    return assignee


# Sample data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "title": "Test Task",
        "description": "A test task",
        "status": "TODO",
        "priority": "MEDIUM"
    }
