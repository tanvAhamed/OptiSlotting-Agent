#!/usr/bin/env python3
"""
OptSlot Agent - Warehouse Management System
Simple runner script for the application
"""

import uvicorn
import sys
import os

def main():
    """Run the FastAPI application"""
    print("🏭 Starting OptSlot Agent - Warehouse Management System...")
    print("📦 Initializing warehouse data...")
    
    # Import to initialize warehouse data
    from models import warehouse
    print(f"✅ Warehouse initialized with {len(warehouse.slots)} slots and {len(warehouse.items)} items")
    
    print("🚀 Starting web server...")
    print("🌐 Access the application at: http://localhost:8000")
    print("📊 API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["./"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 