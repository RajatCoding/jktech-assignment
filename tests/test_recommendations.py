import pytest
from fastapi import status


class TestRecommendations:
    """Test recommendation endpoint."""
    
    def test_get_recommendations(self, client, db_session, test_book):
        """Test getting recommendations."""
        response = client.get("/recommendations")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data
        assert "reason" in data
        assert isinstance(data["recommendations"], list)
    
    def test_get_recommendations_with_genre(self, client, db_session, test_book):
        """Test recommendations with genre filter."""
        response = client.get("/recommendations?preferred_genres=Fiction")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Fiction" in data["reason"]
    
    def test_get_recommendations_with_min_rating(self, client, db_session, test_book, user_token):
        """Test recommendations with minimum rating."""
        # Create a review with high rating
        client.post(
            f"/books/{test_book.id}/reviews",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "review_text": "Excellent!",
                "rating": 5.0
            }
        )
        
        response = client.get("/recommendations?min_rating=4.0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data
    
    def test_get_recommendations_with_user_id(self, client, db_session, test_book, user_token):
        """Test recommendations excluding user's reviewed books."""
        # User creates a review
        client.post(
            f"/books/{test_book.id}/reviews",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "review_text": "Reviewed",
                "rating": 4.0
            }
        )
        
        # Get recommendations for this user
        response = client.get(f"/recommendations?user_id=1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data

