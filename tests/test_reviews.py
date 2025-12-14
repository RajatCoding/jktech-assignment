import pytest
from fastapi import status


class TestReviews:
    """Test review endpoints."""
    
    def test_create_review(self, client, db_session, test_book, user_token):
        """Test creating a review."""
        response = client.post(
            f"/books/{test_book.id}/reviews",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "review_text": "Great book!",
                "rating": 5.0
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["review_text"] == "Great book!"
        assert data["rating"] == 5.0
        assert data["book_id"] == test_book.id
        assert "user_id" in data
    
    def test_create_review_unauthorized(self, client, db_session, test_book):
        """Test creating review without authentication."""
        response = client.post(
            f"/books/{test_book.id}/reviews",
            json={
                "review_text": "Great book!",
                "rating": 5.0
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_review_invalid_book(self, client, user_token):
        """Test creating review for non-existent book."""
        response = client.post(
            "/books/99999/reviews",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "review_text": "Great book!",
                "rating": 5.0
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_review_invalid_rating(self, client, db_session, test_book, user_token):
        """Test creating review with invalid rating."""
        response = client.post(
            f"/books/{test_book.id}/reviews",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "review_text": "Great book!",
                "rating": 10.0  # Invalid (max is 5.0)
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_reviews(self, client, db_session, test_book, user_token):
        """Test getting all reviews for a book."""
        # Create a review first
        client.post(
            f"/books/{test_book.id}/reviews",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "review_text": "Great book!",
                "rating": 5.0
            }
        )
        
        # Get reviews
        response = client.get(f"/books/{test_book.id}/reviews")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["review_text"] == "Great book!"
    
    def test_get_reviews_nonexistent_book(self, client):
        """Test getting reviews for non-existent book."""
        response = client.get("/books/99999/reviews")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_admin_can_create_review(self, client, db_session, test_book, admin_token):
        """Test that admins can also create reviews."""
        response = client.post(
            f"/books/{test_book.id}/reviews",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "review_text": "Admin review",
                "rating": 4.5
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["review_text"] == "Admin review"

