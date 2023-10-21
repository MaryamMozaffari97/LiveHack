import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        session_token TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
