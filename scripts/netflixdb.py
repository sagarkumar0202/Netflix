import sqlite3

conn = sqlite3.connect('../database/users.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
print("✅ users.db created with users table.")
