import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)


class GPTService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.base_url = settings.openai_base_url

    async def generate_summary(self, content: str, book_title=None, author=None) -> str:
        prompt = self._create_summary_prompt(content, book_title, author)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/responses",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": prompt,
                },
            )

            if response.status_code != 200:
                logger.error(response.text)
                raise Exception("OpenAI request failed")

            data = response.json()
            print("----------",data)
            return data["output"][0]["content"][0]["text"]


    async def generate_review_summary(self, reviews: list) -> str:
        """Generate a summary of multiple reviews using GPT model."""
        try:
            if not reviews:
                return "No reviews available."
            
            reviews_text = "\n\n".join([
                f"Rating: {r['rating']}/5.0\nReview: {r['review_text']}"
                for r in reviews
            ])
            
            prompt = f"""Please analyze the following book reviews and provide a concise summary (2-3 sentences) highlighting:
1. Overall sentiment (positive/negative/mixed)
2. Common themes or points mentioned
3. General consensus

Reviews:
{reviews_text}

Summary:"""
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/responses",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": prompt,
                    },
                )
                
                if response.status_code != 200:
                    logger.error(response.text)
                    raise Exception("OpenAI request failed")
                
                data = response.json()
                return data["output"][0]["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error generating review summary: {e}")
            raise Exception(f"Failed to generate review summary: {e}")

    def _create_summary_prompt(self, content, book_title=None, author=None):
        return f"""
Summarize the following book in 3–4 sentences.

Title: {book_title or "N/A"}
Author: {author or "N/A"}

Content:
{content}
"""
gpt_service = GPTService()