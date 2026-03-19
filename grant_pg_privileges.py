import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='031416',
        port=5432,
        database='purecheck_db'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print('Granting full privileges to lord-eren...')
    cursor.execute("GRANT ALL PRIVILEGES ON SCHEMA public TO \"lord-eren\"")
    cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"lord-eren\"")
    cursor.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO \"lord-eren\"")
    cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO \"lord-eren\"")
    cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO \"lord-eren\"")
    cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO \"lord-eren\"")
    cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO \"lord-eren\"")
    print('✓ Permissions granted successfully')
    conn.close()
except Exception as e:
    print(f'Error: {e}')
