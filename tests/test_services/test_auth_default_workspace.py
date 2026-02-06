"""
Tests for default workspace creation on user registration.
"""
from unittest.mock import MagicMock

import pytest

from app.services.auth import AuthService
from app.models.workspaces import Workspace, WorkspaceMember, WorkspaceSetting
from app.db.enums import WorkspaceRole


@pytest.fixture
def mock_email_service():
    return MagicMock()


def test_register_user_creates_default_workspace(db, mock_email_service):
    auth_service = AuthService(db, mock_email_service)

    user, error = auth_service.register_user(
        email="newuser@example.com",
        username="newuser",
        password="SecurePass123!@#",
    )

    assert error is None
    assert user is not None

    workspace = (
        db.query(Workspace)
        .filter(Workspace.owner_id == user.id)
        .one_or_none()
    )

    assert workspace is not None
    assert workspace.name == "newuser's Workspace"
    assert workspace.description == "Your personal workspace"
    assert workspace.status == "ACTIVE"
    assert workspace.is_deleted is False

    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == user.id,
        )
        .one_or_none()
    )

    assert member is not None
    assert member.role == WorkspaceRole.OWNER
    assert member.is_active is True

    settings = (
        db.query(WorkspaceSetting)
        .filter(WorkspaceSetting.workspace_id == workspace.id)
        .one_or_none()
    )

    assert settings is not None
    assert settings.timezone == "UTC"
    assert settings.work_days == "Mon,Tue,Wed,Thu,Fri"
    assert settings.work_hours == '{"start": "09:00", "end": "18:00"}'
