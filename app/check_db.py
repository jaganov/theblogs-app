#!/usr/bin/env python
"""
Script to check database connection
"""
import os
import psycopg2
from urllib.parse import urlparse

def check_database_connection():
    """Check if we can connect to the database"""
    
    # Get database configuration
    db_name = os.environ.get("DB_NAME", "theblogs")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "postgres")
    db_host = os.environ.get("DB_HOST", "postgres")
    db_port = os.environ.get("DB_PORT", "5432")
    
    print(f"Attempting to connect to database:")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  Database: {db_name}")
    print(f"  User: {db_user}")
    
    try:
        # Try to connect
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        
        # Test the connection
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        print(f"✅ Successfully connected to PostgreSQL!")
        print(f"   Version: {version[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False

if __name__ == "__main__":
    check_database_connection() 