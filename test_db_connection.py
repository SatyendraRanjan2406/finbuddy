#!/usr/bin/env python
"""
Test script to verify database connection and psycopg2 installation.
Run this from the Python Debug Console to verify the environment.
"""

import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otp_service.settings')

# Print Python and environment info
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Current directory:", os.getcwd())
print("-" * 50)

# Test psycopg2 import
try:
    import psycopg2
    print("✓ psycopg2 imported successfully")
    print("  Version:", psycopg2.__version__)
except ImportError as e:
    print("✗ psycopg2 import failed:", e)
    print("  Try: pip install psycopg2-binary")
    sys.exit(1)

# Test psycopg (v3) import
try:
    import psycopg
    print("✓ psycopg (v3) also available")
    print("  Version:", psycopg.__version__)
except ImportError:
    print("ℹ psycopg (v3) not available (optional)")

print("-" * 50)

# Test Django setup
try:
    import django
    django.setup()
    print("✓ Django setup successful")
    print("  Django version:", django.get_version())
except Exception as e:
    print("✗ Django setup failed:", e)
    sys.exit(1)

# Test database connection
try:
    from django.db import connection
    print("✓ Database backend imported")
    print("  Engine:", connection.settings_dict.get('ENGINE', 'N/A'))
    print("  Database:", connection.settings_dict.get('NAME', 'N/A'))
    
    # Test actual connection
    connection.ensure_connection()
    print("✓ Database connection successful!")
    
    # Test a simple query
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"  PostgreSQL version: {version[0][:50]}...")
        
except Exception as e:
    print("✗ Database connection failed:", e)
    print("\nTroubleshooting steps:")
    print("1. Ensure PostgreSQL is running: pg_isready")
    print("2. Check .env file has correct database credentials")
    print("3. Verify database exists: psql -l | grep otp_service")
    print("4. Reinstall psycopg2: pip install --force-reinstall psycopg2-binary==2.9.10")
    sys.exit(1)

print("-" * 50)
print("✓ All checks passed! Database is ready to use.")







