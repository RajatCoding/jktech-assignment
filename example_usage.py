"""
Example script demonstrating how to use the Book Management API.
Make sure the API is running before executing this script.
"""
import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def main():
    async with httpx.AsyncClient() as client:
        print("=" * 50)
        print("Book Management API - Example Usage")
        print("=" * 50)
        
        # 1. Create a book
        print("\n1. Creating a book...")
        book_data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Fiction",
            "year_published": 1925,
            "summary": "A classic American novel about the Jazz Age and the American Dream"
        }
        response = await client.post(f"{BASE_URL}/books", json=book_data)
        if response.status_code == 201:
            book = response.json()
            book_id = book["id"]
            print(f"✓ Book created with ID: {book_id}")
        else:
            print(f"✗ Error creating book: {response.text}")
            return
        
        # 2. Get all books
        print("\n2. Retrieving all books...")
        response = await client.get(f"{BASE_URL}/books")
        if response.status_code == 200:
            books = response.json()
            print(f"✓ Found {len(books)} book(s)")
        
        # 3. Get specific book
        print(f"\n3. Retrieving book with ID {book_id}...")
        response = await client.get(f"{BASE_URL}/books/{book_id}")
        if response.status_code == 200:
            book = response.json()
            print(f"✓ Book: {book['title']} by {book['author']}")
        
        # 4. Create users first (required for reviews)
        print(f"\n4. Creating users...")
        user1_data = {
            "username": "user123",
            "email": "user123@example.com",
            "full_name": "John Doe"
        }
        response = await client.post(f"{BASE_URL}/users", json=user1_data)
        if response.status_code == 201:
            user1 = response.json()
            user1_id = user1["id"]
            print(f"✓ User created with ID: {user1_id}")
        else:
            print(f"✗ Error creating user: {response.text}")
            return
        
        user2_data = {
            "username": "user456",
            "email": "user456@example.com",
            "full_name": "Jane Smith"
        }
        response = await client.post(f"{BASE_URL}/users", json=user2_data)
        if response.status_code == 201:
            user2 = response.json()
            user2_id = user2["id"]
            print(f"✓ Second user created with ID: {user2_id}")
        else:
            print(f"✗ Error creating user: {response.text}")
            return
        
        # 5. Add a review
        print(f"\n5. Adding a review for book {book_id}...")
        review_data = {
            "user_id": user1_id,
            "review_text": "A masterpiece of American literature! The writing is beautiful and the story is timeless.",
            "rating": 5.0
        }
        response = await client.post(f"{BASE_URL}/books/{book_id}/reviews", json=review_data)
        if response.status_code == 201:
            review = response.json()
            print(f"✓ Review added with ID: {review['id']}")
        
        # 6. Add another review
        print(f"\n6. Adding another review...")
        review_data2 = {
            "user_id": user2_id,
            "review_text": "Great book but a bit slow in the middle sections.",
            "rating": 4.0
        }
        response = await client.post(f"{BASE_URL}/books/{book_id}/reviews", json=review_data2)
        if response.status_code == 201:
            print("✓ Second review added")
        
        # 7. Get all reviews for the book
        print(f"\n7. Retrieving all reviews for book {book_id}...")
        response = await client.get(f"{BASE_URL}/books/{book_id}/reviews")
        if response.status_code == 200:
            reviews = response.json()
            print(f"✓ Found {len(reviews)} review(s)")
            for review in reviews:
                print(f"  - Rating: {review['rating']}/5.0 by user ID {review['user_id']}")
        
        # 8. Get book summary with aggregated rating
        print(f"\n8. Getting book summary with aggregated rating...")
        response = await client.get(f"{BASE_URL}/books/{book_id}/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"✓ Book: {summary['title']}")
            print(f"  Average Rating: {summary['average_rating']}/5.0")
            print(f"  Total Reviews: {summary['total_reviews']}")
            if summary.get('review_summary'):
                print(f"  Review Summary: {summary['review_summary']}")
        
        # 9. Generate a summary for new content
        print(f"\n9. Generating summary for new book content...")
        summary_request = {
            "content": "A young wizard discovers he has magical powers and attends a school for wizards where he makes friends and faces dark forces.",
            "book_title": "Harry Potter and the Philosopher's Stone",
            "author": "J.K. Rowling"
        }
        response = await client.post(f"{BASE_URL}/generate-summary", json=summary_request)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Generated Summary: {result['summary'][:100]}...")
        else:
            print(f"✗ Error generating summary: {response.text}")
        
        # 10. Get recommendations
        print(f"\n10. Getting book recommendations...")
        response = await client.get(
            f"{BASE_URL}/recommendations",
            params={
                "preferred_genres": "Fiction",
                "min_rating": 4.0,
                "user_id": str(user1_id)  # Use integer user ID
            }
        )
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✓ {recommendations['reason']}")
            print(f"  Found {len(recommendations['recommendations'])} recommendation(s)")
            for book in recommendations['recommendations']:
                print(f"  - {book['title']} by {book['author']}")
        
        print("\n" + "=" * 50)
        print("Example usage completed!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())


