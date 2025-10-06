#!/usr/bin/env python3
# client.py
"""
Small client to exercise the PUT (update) and DELETE endpoints.
Run the API first:
    uvicorn resources:app --reload --port 8000

Then run this script:
    python client.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"  # Unificado al mismo puerto que el servidor principal
UPDATE_URL = f"{BASE_URL}/books/{{book_id}}"
DELETE_URL = f"{BASE_URL}/books/{{book_id}}"

def update_book(book_id: str, update_data: dict):
    url = UPDATE_URL.format(book_id=book_id)
    resp = requests.put(url, json=update_data, timeout=10)
    try:
        data = resp.json()
    except Exception:
        data = {"raw_text": resp.text}
    print(f"[PUT] {url} -> {resp.status_code}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return resp

def delete_book(book_id: str):
    url = DELETE_URL.format(book_id=book_id)
    resp = requests.delete(url, timeout=10)
    try:
        data = resp.json()
    except Exception:
        data = {"raw_text": resp.text}
    print(f"[DELETE] {url} -> {resp.status_code}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return resp

if __name__ == "__main__":
    # Using a real ObjectId from the database
    example_id = "68e141b181e418fc08a87489"  # Clean Architecture book ID

    print("=== TESTING UPDATE OPERATION ===")
    # 1) Example update
    update_payload = {
        "title": "Clean Architecture (Updated via API)",
        "price": 499.0,
        "genres": ["Software", "Architecture", "Design"],
        "stock": 25
    }
    update_book(example_id, update_payload)
    
    print("\n=== VERIFYING UPDATE ===")
    # Verify the update by getting the book
    get_url = f"{BASE_URL}/books/{example_id}"
    resp = requests.get(get_url)
    print(f"[GET] {get_url} -> {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

    print("\n=== TESTING DELETE OPERATION ===")
    # Use the second book for deletion test
    delete_id = "68e140cef8e83da8534b7e13"  # The Pragmatic Programmer ID
    delete_book(delete_id)
