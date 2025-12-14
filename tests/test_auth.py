import pytest
from fastapi import status


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
                "is_admin": False
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data
        assert data["is_admin"] is False
    
    def test_register_admin(self, client):
        """Test admin registration."""
        response = client.post(
            "/register",
            json={
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "is_admin": True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["is_admin"] is True
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        # Register first user
        client.post(
            "/register",
            json={
                "username": "duplicate",
                "email": "first@example.com",
                "password": "pass123"
            }
        )
        
        # Try to register with same username
        response = client.post(
            "/register",
            json={
                "username": "duplicate",
                "email": "second@example.com",
                "password": "pass123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # Register first user
        client.post(
            "/register",
            json={
                "username": "user1",
                "email": "same@example.com",
                "password": "pass123"
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/register",
            json={
                "username": "user2",
                "email": "same@example.com",
                "password": "pass123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, client):
        """Test successful login."""
        # Register user
        client.post(
            "/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "login123"
            }
        )
        
        # Login
        response = client.post(
            "/login",
            data={"username": "loginuser", "password": "login123"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        # Register user
        client.post(
            "/register",
            json={
                "username": "wrongpass",
                "email": "wrong@example.com",
                "password": "correct123"
            }
        )
        
        # Try to login with wrong password
        response = client.post(
            "/login",
            data={"username": "wrongpass", "password": "wrongpass"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/login",
            data={"username": "nonexistent", "password": "pass123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, client, user_token):
        """Test getting current user info."""
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert "password" not in data
    
    def test_get_current_user_no_token(self, client):
        """Test getting user info without token."""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting user info with invalid token."""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

