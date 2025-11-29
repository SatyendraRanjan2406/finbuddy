# Fixing psycopg2 Error in Python Debug Console

If you're seeing this error in the Python Debug Console:
```
django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 or psycopg module
```

## Solution 1: Ensure Correct Python Interpreter

Make sure your IDE is using the same Python interpreter that has psycopg2-binary installed:

1. **Check your Python interpreter:**
   ```bash
   which python
   # Should show: /Users/satyendra/.pyenv/versions/3.12.3/bin/python
   ```

2. **Verify psycopg2 is installed in that environment:**
   ```bash
   python -c "import psycopg2; print(psycopg2.__version__)"
   # Should print: 2.9.10 (dt dec pq3 ext lo64)
   ```

3. **In your IDE (VS Code/Cursor):**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose the interpreter: `/Users/satyendra/.pyenv/versions/3.12.3/bin/python`

## Solution 2: Initialize Django in Debug Console

Before using Django in the Debug Console, always initialize it:

```python
import os
import django

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otp_service.settings')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Setup Django
django.setup()

# Now you can import models and use the database
from finance.models import Product
print(Product.objects.count())
```

## Solution 3: Test Database Connection

Run the test script to verify everything works:

```bash
python test_db_connection.py
```

This will verify:
- ✓ psycopg2 is installed correctly
- ✓ Django can load the PostgreSQL backend
- ✓ Database connection works

## Solution 4: Reinstall psycopg2-binary

If the above doesn't work, reinstall psycopg2-binary:

```bash
pip uninstall -y psycopg2-binary psycopg2
pip install psycopg2-binary==2.9.10
```

## Solution 5: Alternative - Use psycopg3

If psycopg2 continues to cause issues, Django 5.2.8 supports psycopg3:

```bash
pip install psycopg[binary]
```

The database backend will automatically use psycopg3 if available.

## Quick Test in Debug Console

Copy and paste this into your Python Debug Console:

```python
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otp_service.settings')

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Test psycopg2
try:
    import psycopg2
    print(f"✓ psycopg2 {psycopg2.__version__} loaded")
except ImportError as e:
    print(f"✗ psycopg2 import failed: {e}")
    print(f"Python: {sys.executable}")
    sys.exit(1)

# Setup Django
import django
django.setup()

# Test database
from django.db import connection
connection.ensure_connection()
print("✓ Database connection successful!")

# Test models
from finance.models import Product
print(f"✓ Products in database: {Product.objects.count()}")
```

## Common Issues

### Issue: Different Python interpreter in IDE
**Fix:** Select the correct Python interpreter in your IDE settings.

### Issue: Environment variables not loaded
**Fix:** Make sure `.env` file exists in the project root and contains:
```
POSTGRES_DB=otp_service
POSTGRES_USER=satyendra
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Issue: PostgreSQL not running
**Fix:** Start PostgreSQL:
```bash
brew services start postgresql@15
# or
pg_ctl -D /usr/local/var/postgres start
```

### Issue: Database doesn't exist
**Fix:** Create the database:
```bash
createdb otp_service
```



