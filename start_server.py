#!/usr/bin/env python3
"""
Simple server starter for testing
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting server on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)