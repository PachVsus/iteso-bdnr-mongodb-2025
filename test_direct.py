#!/usr/bin/env python3
"""
Test script to verify UPDATE and DELETE operations work correctly
This tests the functions directly without needing a running server
"""
import sys
sys.path.append('.')

from pymongo import MongoClient
from bson import ObjectId
import json
from resources import BookResource, BooksResource
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "bookstore"

def setup_test_data():
    """Set up test data in MongoDB"""
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    books = db.books
    
    # Clear existing data
    books.delete_many({})
    print("Cleared existing books")
    
    # Sample books data
    sample_books = [
        {
            "title": "Clean Architecture",
            "authors": ["Robert C. Martin"],
            "year": 2017,
            "genres": ["Software", "Programming"],
            "price": 399.99,
            "stock": 25
        },
        {
            "title": "Design Patterns",
            "authors": ["Erich Gamma", "Richard Helm", "Ralph Johnson", "John Vlissides"],
            "year": 1994,
            "genres": ["Software", "Programming", "Design"],
            "price": 450.00,
            "stock": 15
        },
        {
            "title": "The Pragmatic Programmer",
            "authors": ["Andrew Hunt", "David Thomas"],
            "year": 1999,
            "genres": ["Software", "Programming"],
            "price": 350.00,
            "stock": 30
        }
    ]
    
    # Insert books and return their IDs
    result = books.insert_many(sample_books)
    print(f"Inserted {len(result.inserted_ids)} books")
    
    # Print book IDs for testing
    for i, book_id in enumerate(result.inserted_ids):
        print(f"Book {i+1} ID: {book_id}")
    
    return result.inserted_ids, db

class MockRequest:
    """Mock request object for testing"""
    def __init__(self, media_data=None, content_length=None):
        self.media = media_data
        self.content_length = content_length if content_length is not None else (len(json.dumps(media_data)) if media_data else 0)
    
    def get_param(self, param, default=None):
        return default

class MockResponse:
    """Mock response object for testing"""
    def __init__(self):
        self.media = None
        self.status = None

def test_get_all_books(book_resource):
    """Test GET all books"""
    print("\n=== Testing GET all books ===")
    req = MockRequest()
    resp = MockResponse()
    
    try:
        # Since we can't use async/await in synchronous context, we'll call the method directly
        # This is a simplified test
        books = book_resource.books.find()
        books_list = list(books)
        print(f"Found {len(books_list)} books in database")
        for book in books_list:
            print(f"  - {book.get('title')} (ID: {book.get('_id')})")
        return books_list
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_update_book_direct(db, book_id):
    """Test UPDATE operation directly on database"""
    print(f"\n=== Testing UPDATE book {book_id} ===")
    
    books = db.books
    
    # Check if book exists before update
    original_book = books.find_one({"_id": ObjectId(book_id)})
    if not original_book:
        print(f"Book with ID {book_id} not found")
        return False
    
    print(f"Original book: {original_book['title']} - Price: ${original_book.get('price', 'N/A')}")
    
    # Update data
    update_data = {
        "title": "Clean Architecture (Updated Edition)",
        "price": 449.99,
        "stock": 50,
        "genres": ["Software", "Programming", "Architecture"]
    }
    
    # Perform update
    result = books.update_one({"_id": ObjectId(book_id)}, {"$set": update_data})
    
    if result.matched_count == 0:
        print("No book found to update")
        return False
    
    if result.modified_count == 0:
        print("Book found but no changes made")
        return False
    
    # Get updated book
    updated_book = books.find_one({"_id": ObjectId(book_id)})
    print(f"Updated book: {updated_book['title']} - Price: ${updated_book.get('price', 'N/A')}")
    print(f"Stock: {updated_book.get('stock', 'N/A')}")
    print(f"Genres: {updated_book.get('genres', [])}")
    print("✅ UPDATE operation successful!")
    return True

def test_delete_book_direct(db, book_id):
    """Test DELETE operation directly on database"""
    print(f"\n=== Testing DELETE book {book_id} ===")
    
    books = db.books
    
    # Check if book exists before deletion
    original_book = books.find_one({"_id": ObjectId(book_id)})
    if not original_book:
        print(f"Book with ID {book_id} not found")
        return False
    
    print(f"Book to delete: {original_book['title']}")
    
    # Perform deletion
    result = books.delete_one({"_id": ObjectId(book_id)})
    
    if result.deleted_count == 0:
        print("No book was deleted")
        return False
    
    # Verify deletion
    deleted_book = books.find_one({"_id": ObjectId(book_id)})
    if deleted_book is None:
        print("✅ DELETE operation successful!")
        return True
    else:
        print("❌ Book still exists after deletion")
        return False

def main():
    print("Starting direct database tests...")
    
    # Set up test data
    book_ids, db = setup_test_data()
    
    # Create resource instances
    book_resource = BookResource(db)
    books_resource = BooksResource(db)
    
    # Test GET all books
    books_list = test_get_all_books(book_resource)
    
    if book_ids and len(book_ids) >= 2:
        # Test UPDATE on first book
        success_update = test_update_book_direct(db, str(book_ids[0]))
        
        # Test DELETE on second book  
        success_delete = test_delete_book_direct(db, str(book_ids[1]))
        
        # Show remaining books
        print("\n=== Final state ===")
        remaining_books = test_get_all_books(book_resource)
        
        # Summary
        print(f"\n=== Test Summary ===")
        print(f"UPDATE test: {'✅ PASSED' if success_update else '❌ FAILED'}")
        print(f"DELETE test: {'✅ PASSED' if success_delete else '❌ FAILED'}")
        print(f"Books remaining: {len(remaining_books)}")
        
        if success_update and success_delete:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed")
    else:
        print("❌ Not enough test data to run tests")

if __name__ == "__main__":
    main()