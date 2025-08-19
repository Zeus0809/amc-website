#!/usr/bin/env python3
"""
Database table creation script for AMC Website

Run this script to create all database tables:
    python create_tables.py

This script creates all tables defined in the models.
"""

import os
import sys
from app import create_app
from models import db

def create_tables():
    """Create all database tables"""
    
    print("🏗️  Creating AMC Website Database Tables...")
    
    # Create app with development config
    app = create_app('development')
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            sys.exit(1)

if __name__ == '__main__':
    create_tables()
    
    print("\n🎉 Database setup complete!")
    print("\n📝 Next steps:")
    print("   1. Run: python app.py")
    print("   2. Visit: http://127.0.0.1:5000")
    print("   3. Register a new account to get started")
