import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='031416',
        port=5432
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if lord-eren user exists
    cursor.execute("SELECT 1 FROM pg_user WHERE usename = 'lord-eren'")
    if cursor.fetchone():
        print('✓ User lord-eren exists')
    else:
        print('Creating user lord-eren...')
        cursor.execute("CREATE USER \"lord-eren\" WITH PASSWORD '031416'")
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE purecheck_db TO \"lord-eren\"")
        cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO \"lord-eren\"")
        cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO \"lord-eren\"")
        print('✓ User lord-eren created successfully')
    
    print('✓ User permissions configured')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
