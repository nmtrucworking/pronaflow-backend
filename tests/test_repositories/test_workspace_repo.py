"""
Unit tests for Workspace Repository (Module 2)
"""
import pytest
from uuid import uuid4
from app.repositories.workspace_repository import WorkspaceRepository
from app.db.models.workspaces import Workspace


@pytest.mark.unit
class TestWorkspaceRepository:
    """Test suite for WorkspaceRepository."""
    
    def test_create_workspace(self, db_session, sample_user_data):
        """Test creating a new workspace."""
        from app.repositories.user_repository import UserRepository
        
        # Create owner user first
        user_repo = UserRepository(db_session)
        owner = user_repo.create(**sample_user_data)
        db_session.commit()
        
        # Create workspace
        repo = WorkspaceRepository(db_session)
        workspace = repo.create(
            name="Test Workspace",
            slug="test-workspace",
            owner_id=owner.id
        )
        
        assert workspace.id is not None
        assert workspace.name == "Test Workspace"
        assert workspace.slug == "test-workspace"
        assert workspace.owner_id == owner.id
        assert workspace.is_active is True
    
    def test_get_by_slug(self, db_session, sample_user_data):
        """Test retrieving workspace by slug."""
        from app.repositories.user_repository import UserRepository
        
        user_repo = UserRepository(db_session)
        owner = user_repo.create(**sample_user_data)
        db_session.commit()
        
        repo = WorkspaceRepository(db_session)
        workspace = repo.create(
            name="Slug Test",
            slug="slug-test",
            owner_id=owner.id
        )
        db_session.commit()
        
        # Retrieve by slug
        found = repo.get_by_slug("slug-test")
        
        assert found is not None
        assert found.id == workspace.id
        assert found.slug == "slug-test"
    
    def test_get_user_workspaces(self, db_session, sample_user_data):
        """Test retrieving all workspaces for a user."""
        from app.repositories.user_repository import UserRepository
        
        user_repo = UserRepository(db_session)
        owner = user_repo.create(**sample_user_data)
        db_session.commit()
        
        repo = WorkspaceRepository(db_session)
        
        # Create multiple workspaces
        for i in range(3):
            repo.create(
                name=f"Workspace {i}",
                slug=f"workspace-{i}",
                owner_id=owner.id
            )
        db_session.commit()
        
        # Get user's workspaces
        workspaces = repo.get_user_workspaces(owner.id)
        
        assert len(workspaces) >= 3
    
    def test_update_workspace(self, db_session, sample_user_data):
        """Test updating workspace information."""
        from app.repositories.user_repository import UserRepository
        
        user_repo = UserRepository(db_session)
        owner = user_repo.create(**sample_user_data)
        db_session.commit()
        
        repo = WorkspaceRepository(db_session)
        workspace = repo.create(
            name="Original Name",
            slug="original",
            owner_id=owner.id
        )
        db_session.commit()
        
        # Update workspace
        updated = repo.update(
            workspace.id,
            name="Updated Name",
            description="New description"
        )
        db_session.commit()
        
        assert updated.name == "Updated Name"
        assert updated.description == "New description"
    
    def test_soft_delete_workspace(self, db_session, sample_user_data):
        """Test soft deleting a workspace."""
        from app.repositories.user_repository import UserRepository
        
        user_repo = UserRepository(db_session)
        owner = user_repo.create(**sample_user_data)
        db_session.commit()
        
        repo = WorkspaceRepository(db_session)
        workspace = repo.create(
            name="Delete Me",
            slug="delete-me",
            owner_id=owner.id
        )
        db_session.commit()
        
        # Soft delete
        result = repo.delete(workspace.id)
        db_session.commit()
        
        assert result is True
        
        # Verify workspace is inactive
        deleted = repo.get(workspace.id)
        assert deleted.is_active is False
        assert deleted.deleted_at is not None
