"""
Unit tests for User Repository (Module 1 - IAM)
"""
import pytest
from uuid import uuid4
from app.db.repositories.user_repo import UserRepository
from app.db.models.users import User, Role, Permission


@pytest.mark.unit
class TestUserRepository:
    """Test suite for UserRepository."""
    
    def test_create_user(self, db_session):
        """Test creating a new user."""
        repo = UserRepository(db_session)
        
        user_data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "password_hash": "hashed_password",
            "is_active": True
        }
        
        user = repo.create(**user_data)
        
        assert user.id is not None
        assert user.email == user_data["email"]
        assert user.full_name == user_data["full_name"]
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_get_by_email(self, db_session):
        """Test retrieving user by email."""
        repo = UserRepository(db_session)
        
        # Create a user first
        user = repo.create(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed"
        )
        db_session.commit()
        
        # Retrieve by email
        found_user = repo.get_by_email("test@example.com")
        
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == user.email
    
    def test_get_by_email_not_found(self, db_session):
        """Test retrieving non-existent user returns None."""
        repo = UserRepository(db_session)
        
        found_user = repo.get_by_email("nonexistent@example.com")
        
        assert found_user is None
    
    def test_update_user(self, db_session):
        """Test updating user information."""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            email="update@example.com",
            full_name="Original Name",
            password_hash="hashed"
        )
        db_session.commit()
        
        # Update user
        updated_user = repo.update(
            user.id,
            full_name="Updated Name",
            is_verified=True
        )
        db_session.commit()
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.is_verified is True
    
    def test_delete_user(self, db_session):
        """Test deleting a user (soft delete)."""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            email="delete@example.com",
            full_name="Delete Me",
            password_hash="hashed"
        )
        db_session.commit()
        user_id = user.id
        
        # Delete user
        result = repo.delete(user_id)
        db_session.commit()
        
        assert result is True
        
        # Verify user is marked inactive
        deleted_user = repo.get(user_id)
        assert deleted_user.is_active is False
    
    def test_list_users(self, db_session):
        """Test listing users with pagination."""
        repo = UserRepository(db_session)
        
        # Create multiple users
        for i in range(5):
            repo.create(
                email=f"user{i}@example.com",
                full_name=f"User {i}",
                password_hash="hashed"
            )
        db_session.commit()
        
        # List users
        users = repo.list(skip=0, limit=10)
        
        assert len(users) == 5
    
    def test_get_active_users(self, db_session):
        """Test retrieving only active users."""
        repo = UserRepository(db_session)
        
        # Create active and inactive users
        repo.create(email="active@example.com", full_name="Active", password_hash="h", is_active=True)
        repo.create(email="inactive@example.com", full_name="Inactive", password_hash="h", is_active=False)
        db_session.commit()
        
        # Get only active users
        active_users = repo.get_active_users()
        
        assert len(active_users) == 1
        assert active_users[0].email == "active@example.com"


@pytest.mark.unit
class TestRoleRepository:
    """Test suite for Role operations."""
    
    def test_create_role(self, db_session):
        """Test creating a role."""
        from app.db.repositories.user_repo import RoleRepository
        
        repo = RoleRepository(db_session)
        
        role = repo.create(
            name="admin",
            description="Administrator role"
        )
        
        assert role.id is not None
        assert role.name == "admin"
        assert role.description == "Administrator role"
    
    def test_get_role_by_name(self, db_session):
        """Test retrieving role by name."""
        from app.db.repositories.user_repo import RoleRepository
        
        repo = RoleRepository(db_session)
        
        # Create role
        role = repo.create(name="editor", description="Editor role")
        db_session.commit()
        
        # Retrieve by name
        found_role = repo.get_by_name("editor")
        
        assert found_role is not None
        assert found_role.id == role.id
        assert found_role.name == "editor"
