import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)


class LlamaService:
    def __init__(self):
        self.api_key = settings.open_router_api_key
        self.model = settings.llm_model
        self.base_url = settings.llm_base_url.rstrip("/")

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")

    async def generate_summary(self, content: str, book_title=None, author=None) -> str:
        """
        Generate a book summary using Llama-3 via OpenRouter.
        """

        prompt = self._create_summary_prompt(content, book_title, author)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "JK Tech Book System"
        }

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that summarizes books clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "max_tokens": 400
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=body
                )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise Exception("Failed to generate book summary.")

    async def generate_review_summary(self, reviews: list) -> str:
        """
        Summarize multiple reviews using Llama-3.
        """

        if not reviews:
            return "No reviews available."

        reviews_text = "\n\n".join([
            f"Rating: {r['rating']}/5\nReview: {r['review_text']}"
            for r in reviews
        ])

        prompt = f"""
Analyze the following book reviews and produce a concise 2–3 sentence summary including:

• Overall sentiment  
• Frequently mentioned themes  
• General reader consensus  

Reviews:
{reviews_text}
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "JK Tech Book System"
        }

        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You summarize customer feedback objectively and clearly."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 400
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=body
                )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Review summary failed: {e}")
            raise Exception("Failed to generate review summary.")

    def _create_summary_prompt(self, content, book_title=None, author=None):
        return f"""
Summarize the following book in 3–4 clear sentences.

Title: {book_title or "Unknown"}
Author: {author or "Unknown"}

Content:
{content}
"""
llama_service = LlamaService()