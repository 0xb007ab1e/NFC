"""
User API route tests for the NFC Reader/Writer System PC Server.

This module contains tests for the user management API endpoints.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session
from server.api.routes.user import verify_password

# Test utilities
from server.tests.conftest import async_client, test_db_session
from server.api.app import app
from server.db.models.user import User


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "is_active": True,
        "is_admin": False,
        "permissions": ["read", "write"],
        "first_name": "Test",
        "last_name": "User",
        "notes": "Test user for unit testing",
        "user_metadata": {"department": "Testing"}
    }


@pytest.fixture
def admin_user_data() -> Dict[str, Any]:
    """Sample admin user data for testing."""
    return {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "is_active": True,
        "is_admin": True,
        "permissions": ["read", "write", "admin"],
        "first_name": "Admin",
        "last_name": "User",
        "notes": "Admin user for testing",
        "user_metadata": {"department": "Administration"}
    }


class TestUserCRUD:
    """Test cases for User CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, async_client: AsyncClient, test_db_session: Session, sample_user_data: Dict[str, Any]):
        """Test successful user creation (happy path)."""
        # Test 1: Happy path - POST /api/v1/users creating a user with unique username/email → 201 and persisted
        response = await async_client.post("/api/v1/users/", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["is_active"] == sample_user_data["is_active"]
        assert data["is_admin"] == sample_user_data["is_admin"]
        assert data["permissions"] == sample_user_data["permissions"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert data["notes"] == sample_user_data["notes"]
        assert data["user_metadata"] == sample_user_data["user_metadata"]
        
        # Password should not be in response
        assert "password" not in data
        assert "password_hash" not in data
        
        # Verify database entry
        user_id = uuid.UUID(data["id"])
        db_user = test_db_session.query(User).filter(User.id == user_id).first()
        assert db_user is not None
        assert db_user.username == sample_user_data["username"]
        assert db_user.email == sample_user_data["email"]
        # Password should be hashed
        assert db_user.password_hash != sample_user_data["password"]


    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test user creation with duplicate username returns conflict error."""
        # Create the first user
        response1 = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert response1.status_code == 201
        
        # Attempt to create user with same username
        response2 = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert response2.status_code == 409
        
        error_data = response2.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()
        assert "username" in error_data["detail"].lower()
        assert sample_user_data["username"] in error_data["detail"]

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test user creation with duplicate email returns conflict error."""
        # Create first user
        response1 = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert response1.status_code == 201
        
        # Attempt to create user with same email but different username
        duplicate_email_data = sample_user_data.copy()
        duplicate_email_data["username"] = "another_user"
        
        response2 = await async_client.post("/api/v1/users/", json=duplicate_email_data)
        assert response2.status_code == 409
        
        error_data = response2.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()
        assert "email" in error_data["detail"].lower()
        assert sample_user_data["email"] in error_data["detail"]

    @pytest.mark.asyncio
    async def test_get_users_list_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any],
        admin_user_data: Dict[str, Any]
    ):
        """Test successful retrieval of users list with pagination and filtering."""
        # Create multiple users
        await async_client.post("/api/v1/users/", json=sample_user_data)
        await async_client.post("/api/v1/users/", json=admin_user_data)
        
        # Retrieve all users
        response = await async_client.get("/api/v1/users/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Test pagination
        response_paginated = await async_client.get("/api/v1/users/?skip=0&limit=1")
        assert response_paginated.status_code == 200
        paginated_data = response_paginated.json()
        assert len(paginated_data) == 1
        
        # Test filtering by active status
        response_active = await async_client.get("/api/v1/users/?is_active=true")
        assert response_active.status_code == 200
        active_data = response_active.json()
        assert all(user["is_active"] for user in active_data)
        
        # Test filtering by admin status
        response_admin = await async_client.get("/api/v1/users/?is_admin=true")
        assert response_admin.status_code == 200
        admin_data = response_admin.json()
        assert all(user["is_admin"] for user in admin_data)
        assert any(user["username"] == admin_user_data["username"] for user in admin_data)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test successful retrieval of a user by ID."""
        # Create user first
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        
        # Retrieve user
        response = await async_client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test retrieval of non-existent user returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/v1/users/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test successful retrieval of a user by username."""
        # Create user first
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        
        # Retrieve user by username
        username = sample_user_data["username"]
        response = await async_client.get(f"/api/v1/users/by-username/{username}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == username
        assert data["email"] == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test retrieval of non-existent username returns 404."""
        response = await async_client.get("/api/v1/users/by-username/nonexistent_user")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_user_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test successful user update."""
        # Create user first
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        
        # Update user
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "notes": "Updated notes",
            "is_admin": True,
            "permissions": ["read", "write", "admin"],
            "user_metadata": {"department": "Updated Department", "role": "Manager"}
        }
        
        response = await async_client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == user_id
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert data["notes"] == update_data["notes"]
        assert data["is_admin"] == update_data["is_admin"]
        assert data["permissions"] == update_data["permissions"]
        assert data["user_metadata"] == update_data["user_metadata"]
        
        # Verify the email remained unchanged
        assert data["email"] == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any],
        admin_user_data: Dict[str, Any]
    ):
        """Test updating user with an email that already exists returns conflict."""
        # Create two users
        user1_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert user1_response.status_code == 201
        user1_id = user1_response.json()["id"]
        
        user2_response = await async_client.post("/api/v1/users/", json=admin_user_data)
        assert user2_response.status_code == 201
        
        # Try to update user1 with user2's email
        update_data = {
            "email": admin_user_data["email"]
        }
        
        response = await async_client.put(f"/api/v1/users/{user1_id}", json=update_data)
        assert response.status_code == 409
        
        error_data = response.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()
        assert "email" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_user_password_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test successful password update."""
        # Create user first
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        
        # Get original password hash
        original_user = test_db_session.query(User).filter(User.id == uuid.UUID(user_id)).first()
        original_hash = original_user.password_hash
        
        # Update password
        new_password = "NewSecurePass456!"
        password_data = {
            "current_password": sample_user_data["password"],
            "new_password": new_password
        }
        
        response = await async_client.patch(f"/api/v1/users/{user_id}/password", json=password_data)
        assert response.status_code == 200
        
        # Verify password is updated (hash should be different)
        db_user = test_db_session.query(User).filter(User.id == uuid.UUID(user_id)).first()
        assert db_user.password_hash != original_hash
        
        # Verify new password can be verified with the hash
        assert verify_password(new_password, db_user.password_hash) is True
        # Verify old password no longer works
        assert verify_password(sample_user_data["password"], db_user.password_hash) is False

    @pytest.mark.asyncio
    async def test_update_user_password_incorrect_current(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test password update with incorrect current password fails."""
        # Create user first
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        
        # Update password with wrong current password
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePass456!"
        }
        
        response = await async_client.patch(f"/api/v1/users/{user_id}/password", json=password_data)
        assert response.status_code == 400
        
        error_data = response.json()
        assert "detail" in error_data
        assert "incorrect" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test successful user deletion."""
        # Create user first
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        
        # Delete user
        response = await async_client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = await async_client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_activate_deactivate_user(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test activating and deactivating a user."""
        # Create user first
        sample_user_data["is_active"] = False
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        assert create_response.json()["is_active"] is False
        
        # Activate user
        activate_response = await async_client.patch(f"/api/v1/users/{user_id}/activate")
        assert activate_response.status_code == 200
        assert activate_response.json()["is_active"] is True
        
        # Deactivate user
        deactivate_response = await async_client.patch(f"/api/v1/users/{user_id}/deactivate")
        assert deactivate_response.status_code == 200
        assert deactivate_response.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_unlock_user(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_user_data: Dict[str, Any]
    ):
        """Test unlocking a user account."""
        # Create user first
        create_response = await async_client.post("/api/v1/users/", json=sample_user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]
        
        # Manually lock the user in the database
        user = test_db_session.query(User).filter(User.id == uuid.UUID(user_id)).first()
        user.failed_login_attempts = 5
        user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        test_db_session.commit()
        
        # Unlock user
        unlock_response = await async_client.patch(f"/api/v1/users/{user_id}/unlock")
        assert unlock_response.status_code == 200
        
        # Verify user is unlocked
        data = unlock_response.json()
        assert data["failed_login_attempts"] == 0
        assert data["locked_until"] is None
