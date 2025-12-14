import pytest
from unittest.mock import AsyncMock, Mock, patch
from llama_service import GPTService


class TestGPTService:
    """Test GPT service."""
    
    @pytest.fixture
    def gpt_service(self):
        """Create GPT service instance."""
        with patch('llama_service.settings') as mock_settings:
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = None
            service = GPTService()
            return service
    
    @pytest.mark.asyncio
    async def test_generate_summary_success(self, gpt_service):
        """Test successful summary generation."""
        mock_response_data = {
            "output": [{
                "content": [{
                    "text": "This is a test summary of the book."
                }]
            }]
        }
        
        # Create a proper mock response (json() is synchronous in httpx)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.text = ""
        
        # Mock the AsyncClient context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            summary = await gpt_service.generate_summary(
                "A story about a wizard",
                "Test Book",
                "Test Author"
            )
            
            assert summary == "This is a test summary of the book."
    
    @pytest.mark.asyncio
    async def test_generate_review_summary_success(self, gpt_service):
        """Test successful review summary generation."""
        mock_response_data = {
            "output": [{
                "content": [{
                    "text": "Reviews are generally positive with an average rating."
                }]
            }]
        }
        
        reviews = [
            {"rating": 5.0, "review_text": "Great book!"},
            {"rating": 4.0, "review_text": "Good read"}
        ]
        
        # Create a proper mock response (json() is synchronous in httpx)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.text = ""
        
        # Mock the AsyncClient context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            summary = await gpt_service.generate_review_summary(reviews)
            
            assert "positive" in summary.lower() or "rating" in summary.lower()
    
    @pytest.mark.asyncio
    async def test_generate_review_summary_empty(self, gpt_service):
        """Test review summary with empty reviews."""
        summary = await gpt_service.generate_review_summary([])
        assert summary == "No reviews available."
    
    @pytest.mark.asyncio
    async def test_generate_summary_api_error(self, gpt_service):
        """Test summary generation with API error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value.post = AsyncMock(side_effect=Exception("API Error"))
            mock_client.return_value = mock_client_instance
            
            with pytest.raises(Exception) as exc_info:
                await gpt_service.generate_summary("Test content")
            
            # The actual error will be raised, not wrapped
            assert "API Error" in str(exc_info.value) or "Failed" in str(exc_info.value)

