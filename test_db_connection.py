#!/usr/bin/env python
import os
import sys
import django

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print('[OK] PostgreSQL Connection Successful!')
        print(f'    Version: {version.split()[0:3]}')
        print()
        print('[OK] Running migrations...')
        
    # Run migrations
    execute_from_command_line(['manage.py', 'migrate'])
    
except Exception as e:
    print(f'[ERROR] {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
