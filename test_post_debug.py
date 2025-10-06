#!/usr/bin/env python3
"""
Debug script to test POST operation directly
"""
import sys
sys.path.append('.')

from pymongo import MongoClient
import json
import asyncio
from resources import BooksResource
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "bookstore"

class MockRequest:
    """Mock request object for testing"""
    def __init__(self, media_data=None):
        self._media_data = media_data
        self.content_length = len(json.dumps(media_data)) if media_data else 0
    
    async def get_media(self):
        return self._media_data

class MockResponse:
    """Mock response object for testing"""
    def __init__(self):
        self.media = None
        self.status = None

async def test_post_operation():
    """Test POST operation directly"""
    print("Testing POST operation directly...")
    
    # Set up database connection
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # Create resource instance
    books_resource = BooksResource(db)
    
    # Test data - simple book
    test_book = {
        "title": "Test Book Direct",
        "authors": ["Test Author"],
        "year": 2023
    }
    
    print(f"Test book data: {json.dumps(test_book, indent=2)}")
    
    # Create mock request and response
    req = MockRequest(test_book)
    resp = MockResponse()
    
    try:
        # Call the POST method directly
        await books_resource.on_post(req, resp)
        
        print("✅ POST operation successful!")
        print(f"Response status: {resp.status}")
        print(f"Response media: {json.dumps(resp.media, indent=2)}")
        
    except Exception as e:
        print(f"❌ POST operation failed: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_post_operation())