#!/usr/bin/env python3
# resources.py
import falcon
import json
from pymongo import MongoClient
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


def _oid(book_id: str) -> ObjectId:
    """Convert string to ObjectId, raise HTTP 422 if invalid."""
    if not ObjectId.is_valid(book_id):
        raise falcon.HTTPUnprocessableEntity(
            title="Invalid ObjectId",
            description=f"book_id '{book_id}' is not a valid ObjectId"
        )
    return ObjectId(book_id)


def _serialize(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if not doc:
        return doc
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    return doc


class BookResource:
    """Handles single book operations: GET, PUT, DELETE /books/{book_id}"""
    
    def __init__(self, db):
        self.books = db.books
    
    async def on_get(self, req, resp, book_id):
        """GET /books/{book_id} - Get a single book by ID"""
        try:
            oid = _oid(book_id)
            book = self.books.find_one({"_id": oid})
            
            if not book:
                raise falcon.HTTPNotFound(
                    title="Book not found",
                    description=f"Book with id '{book_id}' not found"
                )
            
            resp.media = _serialize(book)
            logger.info(f"Retrieved book {book_id}")
            
        except ValueError as e:
            raise falcon.HTTPBadRequest(
                title="Invalid request",
                description=str(e)
            )
    
    async def on_put(self, req, resp, book_id):
        """PUT /books/{book_id} - Update a book by ID"""
        try:
            oid = _oid(book_id)
            
            # Get update data from request body
            if not req.content_length:
                raise falcon.HTTPBadRequest(
                    title="Empty request body",
                    description="Request body is required for update operation"
                )
            
            try:
                update_data = await req.get_media()
            except Exception as e:
                raise falcon.HTTPBadRequest(
                    title="Invalid JSON",
                    description="Request body must be valid JSON"
                )
            
            if not update_data:
                raise falcon.HTTPBadRequest(
                    title="No fields to update",
                    description="At least one field must be provided for update"
                )
            
            # Remove _id if present in update data (shouldn't be updated)
            update_data.pop("_id", None)
            
            # Validate numeric fields
            if "year" in update_data and (not isinstance(update_data["year"], int) or update_data["year"] < 0):
                raise falcon.HTTPBadRequest(
                    title="Invalid year",
                    description="Year must be a positive integer"
                )
            
            if "price" in update_data and (not isinstance(update_data["price"], (int, float)) or update_data["price"] < 0):
                raise falcon.HTTPBadRequest(
                    title="Invalid price",
                    description="Price must be a positive number"
                )
            
            if "stock" in update_data and (not isinstance(update_data["stock"], int) or update_data["stock"] < 0):
                raise falcon.HTTPBadRequest(
                    title="Invalid stock",
                    description="Stock must be a non-negative integer"
                )
            
            # Perform the update
            result = self.books.update_one({"_id": oid}, {"$set": update_data})
            
            if result.matched_count == 0:
                raise falcon.HTTPNotFound(
                    title="Book not found",
                    description=f"Book with id '{book_id}' not found"
                )
            
            # Return the updated document
            updated_book = self.books.find_one({"_id": oid})
            resp.media = {
                "message": "Book updated successfully",
                "book": _serialize(updated_book)
            }
            logger.info(f"Updated book {book_id}")
            
        except ValueError as e:
            raise falcon.HTTPBadRequest(
                title="Invalid request",
                description=str(e)
            )
    
    async def on_delete(self, req, resp, book_id):
        """DELETE /books/{book_id} - Delete a book by ID"""
        try:
            oid = _oid(book_id)
            
            # Perform the deletion
            result = self.books.delete_one({"_id": oid})
            
            if result.deleted_count == 0:
                raise falcon.HTTPNotFound(
                    title="Book not found",
                    description=f"Book with id '{book_id}' not found"
                )
            
            resp.media = {
                "message": "Book deleted successfully",
                "deleted_id": str(oid)
            }
            logger.info(f"Deleted book {book_id}")
            
        except ValueError as e:
            raise falcon.HTTPBadRequest(
                title="Invalid request",
                description=str(e)
            )


class BooksResource:
    """Handles collection operations: GET, POST /books"""
    
    def __init__(self, db):
        self.books = db.books
    
    async def on_get(self, req, resp):
        """GET /books - Get all books"""
        try:
            # Get query parameters for pagination
            limit = int(req.get_param('limit', default=50))
            skip = int(req.get_param('skip', default=0))
            
            # Validate pagination parameters
            if limit < 0 or skip < 0:
                raise falcon.HTTPBadRequest(
                    title="Invalid pagination",
                    description="Limit and skip must be non-negative integers"
                )
            
            if limit > 1000:
                limit = 1000  # Cap the limit for performance
            
            # Get books from database
            cursor = self.books.find().skip(skip).limit(limit)
            books = [_serialize(book) for book in cursor]
            
            # Get total count
            total = self.books.count_documents({})
            
            resp.media = {
                "books": books,
                "total": total,
                "limit": limit,
                "skip": skip
            }
            logger.info(f"Retrieved {len(books)} books (total: {total})")
            
        except ValueError as e:
            raise falcon.HTTPBadRequest(
                title="Invalid request",
                description=str(e)
            )
    
    async def on_post(self, req, resp):
        """POST /books - Create a new book"""
        try:
            # Get book data from request body
            if not req.content_length:
                raise falcon.HTTPBadRequest(
                    title="Empty request body",
                    description="Request body is required for book creation"
                )
            
            try:
                book_data = await req.get_media()
            except Exception as e:
                raise falcon.HTTPBadRequest(
                    title="Invalid JSON",
                    description="Request body must be valid JSON"
                )
            
            if not book_data:
                raise falcon.HTTPBadRequest(
                    title="No book data",
                    description="Book data must be provided"
                )
            
            # Validate required fields
            required_fields = ["title"]
            for field in required_fields:
                if field not in book_data:
                    raise falcon.HTTPBadRequest(
                        title="Missing required field",
                        description=f"Field '{field}' is required"
                    )
            
            # Remove _id if present (will be auto-generated)
            book_data.pop("_id", None)
            
            # Validate numeric fields (same as PUT method)
            if "year" in book_data and (not isinstance(book_data["year"], int) or book_data["year"] < 0):
                raise falcon.HTTPBadRequest(
                    title="Invalid year",
                    description="Year must be a positive integer"
                )
            
            if "price" in book_data and (not isinstance(book_data["price"], (int, float)) or book_data["price"] < 0):
                raise falcon.HTTPBadRequest(
                    title="Invalid price",
                    description="Price must be a positive number"
                )
            
            if "stock" in book_data and (not isinstance(book_data["stock"], int) or book_data["stock"] < 0):
                raise falcon.HTTPBadRequest(
                    title="Invalid stock",
                    description="Stock must be a non-negative integer"
                )
            
            # Insert the book
            result = self.books.insert_one(book_data)
            
            # Return the created book
            created_book = self.books.find_one({"_id": result.inserted_id})
            resp.status = falcon.HTTP_201
            resp.media = {
                "message": "Book created successfully",
                "book": _serialize(created_book)
            }
            logger.info(f"Created book with id {result.inserted_id}")
            
        except falcon.HTTPError:
            # Re-raise Falcon HTTP errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in POST /books: {e}")
            raise falcon.HTTPInternalServerError(
                title="Internal Server Error",
                description=f"An unexpected error occurred: {str(e)}"
            )
