import pytest
from fastapi import status


class TestBooks:
    """Test book endpoints."""
    
    def test_create_book_as_admin(self, client, admin_token):
        """Test creating a book as admin."""
        response = client.post(
            "/books",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "New Book",
                "author": "Author Name",
                "genre": "Fiction",
                "year_published": 2024,
                "summary": "A great book"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Book"
        assert data["author"] == "Author Name"
        assert "id" in data
    
    def test_create_book_as_normal_user(self, client, user_token):
        """Test that normal users cannot create books."""
        response = client.post(
            "/books",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "New Book",
                "author": "Author Name",
                "genre": "Fiction",
                "year_published": 2024
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in response.json()["detail"]
    
    def test_create_book_unauthorized(self, client):
        """Test creating book without authentication."""
        response = client.post(
            "/books",
            json={
                "title": "New Book",
                "author": "Author",
                "genre": "Fiction",
                "year_published": 2024
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_all_books(self, client, db_session, test_book):
        """Test getting all books."""
        response = client.get("/books")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_all_books_with_filter(self, client, db_session, test_book):
        """Test getting books with genre filter."""
        response = client.get("/books?genre=Fiction")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(book["genre"] == "Fiction" for book in data)
    
    def test_get_book_by_id(self, client, db_session, test_book):
        """Test getting a specific book."""
        response = client.get(f"/books/{test_book.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_book.id
        assert data["title"] == test_book.title
    
    def test_get_book_not_found(self, client):
        """Test getting non-existent book."""
        response = client.get("/books/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_book(self, client, db_session, test_book, admin_token):
        """Test updating a book."""
        # Note: Update endpoint currently doesn't require auth, but should work
        response = client.put(
            f"/books/{test_book.id}",
            json={"title": "Updated Title"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
    
    def test_delete_book(self, client, db_session, test_book, admin_token):
        """Test deleting a book as admin."""
        response = client.delete(
            f"/books/{test_book.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify book is deleted
        response = client.get(f"/books/{test_book.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_book_as_normal_user(self, client, db_session, test_book, user_token):
        """Test that normal users cannot delete books."""
        response = client.delete(
            f"/books/{test_book.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in response.json()["detail"]
    
    def test_delete_book_unauthorized(self, client, db_session, test_book):
        """Test deleting book without authentication."""
        response = client.delete(f"/books/{test_book.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_book_invalid_year(self, client, admin_token):
        """Test creating book with invalid year."""
        response = client.post(
            "/books",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Book",
                "author": "Author",
                "genre": "Fiction",
                "year_published": 999  # Invalid (too low)
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

