#!/usr/bin/env python3

import uvicorn
from database import init_db

if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Run the FastAPI server
    print("Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )