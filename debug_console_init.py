# Copy and paste this into your Python Debug Console to fix psycopg2 issues

import os
import sys

# Check Python interpreter
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otp_service.settings')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded from .env")
except Exception as e:
    print(f"⚠ Could not load .env: {e}")

# Test psycopg2
try:
    import psycopg2
    print(f"✓ psycopg2 {psycopg2.__version__} imported successfully")
except ImportError as e:
    print(f"✗ psycopg2 import failed: {e}")
    print(f"  Python path: {sys.path[:3]}")
    print(f"  Try: pip install psycopg2-binary==2.9.10")
    raise

# Initialize Django
import django
django.setup()
print(f"✓ Django {django.get_version()} initialized")

# Test database connection
from django.db import connection
connection.ensure_connection()
print("✓ Database connection successful!")

print("\n✓ Ready to use Django models!")
