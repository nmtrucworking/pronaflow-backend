"""
Integration tests for Authentication API endpoints (Module 1)
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
class TestAuthenticationAPI:
    """Test suite for authentication endpoints."""
    
    def test_register_user(self, client: TestClient):
        """Test user registration endpoint."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "SecurePassword123!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password" not in data
    
    def test_register_duplicate_email(self, client: TestClient):
        """Test registering with duplicate email returns error."""
        user_data = {
            "email": "duplicate@example.com",
            "full_name": "First User",
            "password": "SecurePassword123!"
        }
        
        # First registration
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Duplicate registration
        response2 = client.post("/api/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    def test_login_success(self, client: TestClient):
        """Test successful login."""
        # Register user first
        client.post(
            "/api/auth/register",
            json={
                "email": "login@example.com",
                "full_name": "Login User",
                "password": "SecurePassword123!"
            }
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            data={
                "username": "login@example.com",
                "password": "SecurePassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient):
        """Test login with wrong password."""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "email": "wrongpw@example.com",
                "full_name": "Wrong PW",
                "password": "SecurePassword123!"
            }
        )
        
        # Login with wrong password
        response = client.post(
            "/api/auth/login",
            data={
                "username": "wrongpw@example.com",
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient):
        """Test getting current user profile."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={
                "email": "profile@example.com",
                "full_name": "Profile User",
                "password": "SecurePassword123!"
            }
        )
        
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": "profile@example.com",
                "password": "SecurePassword123!"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Get profile
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "profile@example.com"
        assert data["full_name"] == "Profile User"


@pytest.mark.api
class TestWorkspaceAPI:
    """Test suite for workspace endpoints."""
    
    @pytest.fixture
    def auth_headers(self, client: TestClient):
        """Create authenticated user and return headers."""
        client.post(
            "/api/auth/register",
            json={
                "email": "workspace@example.com",
                "full_name": "Workspace User",
                "password": "SecurePassword123!"
            }
        )
        
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": "workspace@example.com",
                "password": "SecurePassword123!"
            }
        )
        
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_workspace(self, client: TestClient, auth_headers):
        """Test creating a workspace."""
        response = client.post(
            "/api/workspaces",
            json={
                "name": "My Workspace",
                "slug": "my-workspace",
                "description": "Test workspace"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Workspace"
        assert data["slug"] == "my-workspace"
        assert "id" in data
    
    def test_list_workspaces(self, client: TestClient, auth_headers):
        """Test listing user's workspaces."""
        # Create some workspaces
        for i in range(3):
            client.post(
                "/api/workspaces",
                json={
                    "name": f"Workspace {i}",
                    "slug": f"workspace-{i}"
                },
                headers=auth_headers
            )
        
        # List workspaces
        response = client.get("/api/workspaces", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 3
    
    def test_get_workspace_by_slug(self, client: TestClient, auth_headers):
        """Test retrieving workspace by slug."""
        # Create workspace
        create_response = client.post(
            "/api/workspaces",
            json={
                "name": "Slug Test",
                "slug": "slug-test"
            },
            headers=auth_headers
        )
        
        workspace_id = create_response.json()["id"]
        
        # Get by slug
        response = client.get(
            f"/api/workspaces/slug/slug-test",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workspace_id
        assert data["slug"] == "slug-test"
