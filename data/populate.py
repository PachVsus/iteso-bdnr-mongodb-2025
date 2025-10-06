#!/usr/bin/env python3
import csv
import requests
import os
import json

BASE_URL = "http://localhost:8000"

def convert_to_number(value, field_name, default=None):
    """Convert string to appropriate numeric type, with error handling"""
    if not value or value.strip() == '':
        return default
    
    try:
        # For fields that should be integers
        if field_name in ['num_pages', 'ratings_count', 'text_reviews_count']:
            return int(float(value))  # float first to handle decimals, then int
        # For fields that can be floats
        elif field_name in ['average_rating']:
            return float(value)
        # For publication year (extract from date if needed)
        elif field_name == 'publication_date':
            # Try to extract year from date string like "9/16/2006"
            if '/' in value:
                parts = value.split('/')
                if len(parts) >= 3:
                    return int(parts[-1])  # Take the last part as year
            return None
    except (ValueError, TypeError):
        print(f"Warning: Could not convert '{value}' to number for field '{field_name}'")
        return default
    
    return value

def clean_book_data(book):
    """Clean and transform book data from CSV to API format"""
    # Remove the bookID field
    if "bookID" in book:
        del book["bookID"]
    
    # Split authors by "/"
    if "authors" in book:
        book["authors"] = [author.strip() for author in book["authors"].split("/")]
    
    # Convert numeric fields
    numeric_conversions = {
        'average_rating': convert_to_number(book.get('average_rating'), 'average_rating'),
        'num_pages': convert_to_number(book.get('num_pages'), 'num_pages'),
        'ratings_count': convert_to_number(book.get('ratings_count'), 'ratings_count'),
        'text_reviews_count': convert_to_number(book.get('text_reviews_count'), 'text_reviews_count')
    }
    
    # Update book with converted values, removing None values
    for key, value in numeric_conversions.items():
        if value is not None:
            book[key] = value
        elif key in book:
            del book[key]  # Remove fields that couldn't be converted
    
    # Handle publication date - try to extract year
    if 'publication_date' in book:
        year = convert_to_number(book['publication_date'], 'publication_date')
        if year:
            book['year'] = year
        # Keep the original publication_date as string
    
    # Clean up empty string values
    book = {k: v for k, v in book.items() if v != '' and v is not None}
    
    return book

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "books.csv")
    
    success_count = 0
    error_count = 0
    
    print(f"Reading books from: {csv_path}")
    
    try:
        with open(csv_path, encoding='utf-8') as fd:
            books_csv = csv.DictReader(fd)
            for i, book in enumerate(books_csv, 1):
                try:
                    # Clean and transform the book data
                    cleaned_book = clean_book_data(book)
                    
                    # Make the API request
                    response = requests.post(f"{BASE_URL}/books", json=cleaned_book, timeout=10)
                    
                    if response.ok:
                        print(f"✅ {i}: Added book: {cleaned_book.get('title', 'Unknown')}")
                        success_count += 1
                    else:
                        print(f"❌ {i}: Failed to post book (Status {response.status_code})")
                        print(f"   Title: {cleaned_book.get('title', 'Unknown')}")
                        try:
                            error_details = response.json()
                            print(f"   Error: {error_details}")
                        except:
                            print(f"   Error: {response.text}")
                        error_count += 1
                        
                        # Show first few failed books for debugging
                        if error_count <= 3:
                            print(f"   Book data: {json.dumps(cleaned_book, indent=2)[:500]}...")
                
                except requests.exceptions.RequestException as e:
                    print(f"❌ {i}: Connection error for book: {book.get('title', 'Unknown')}")
                    print(f"   Error: {e}")
                    error_count += 1
                
                except Exception as e:
                    print(f"❌ {i}: Unexpected error for book: {book.get('title', 'Unknown')}")
                    print(f"   Error: {e}")
                    error_count += 1
                
                # Stop after 10 errors to avoid spam
                if error_count >= 10:
                    print("❌ Too many errors, stopping...")
                    break
    
    except FileNotFoundError:
        print(f"❌ Error: Could not find file {csv_path}")
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successfully added: {success_count} books")
    print(f"   ❌ Failed: {error_count} books")

if __name__ == "__main__":
    main()