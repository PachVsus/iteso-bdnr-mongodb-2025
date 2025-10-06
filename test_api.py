#!/usr/bin/env python3
"""
Quick test script to insert some sample data and test UPDATE/DELETE operations
"""
import requests
import json
from pymongo import MongoClient
from bson import ObjectId

# Configuration
BASE_URL = "http://localhost:8000"  # Unificado con el servidor principal
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "bookstore"
COLLECTION_NAME = "books"

def create_sample_books():
    """Insert sample books directly into MongoDB"""
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    books = db[COLLECTION_NAME]
    
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
    
    return result.inserted_ids

def test_get_books():
    """Test GET /books endpoint"""
    print("\n=== Testing GET /books ===")
    try:
        response = requests.get(f"{BASE_URL}/books")
        print(f"Status: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Found {len(data.get('books', []))} books")
            for book in data.get('books', []):
                print(f"  - {book.get('title')} (ID: {book.get('_id')})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {e}")

def test_update_book(book_id):
    """Test PUT /books/{book_id} endpoint"""
    print(f"\n=== Testing PUT /books/{book_id} ===")
    
    update_data = {
        "title": "Clean Architecture (Updated Edition)",
        "price": 449.99,
        "stock": 50,
        "genres": ["Software", "Programming", "Architecture"]
    }
    
    try:
        response = requests.put(f"{BASE_URL}/books/{book_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")

def test_delete_book(book_id):
    """Test DELETE /books/{book_id} endpoint"""
    print(f"\n=== Testing DELETE /books/{book_id} ===")
    
    try:
        response = requests.delete(f"{BASE_URL}/books/{book_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("Starting comprehensive test...")
    
    # Insert sample data
    book_ids = create_sample_books()
    
    # Test GET
    test_get_books()
    
    if book_ids:
        # Test UPDATE on first book
        test_update_book(str(book_ids[0]))
        
        # Test DELETE on second book
        test_delete_book(str(book_ids[1]))
        
        # Test GET again to see changes
        test_get_books()

if __name__ == "__main__":
    main()