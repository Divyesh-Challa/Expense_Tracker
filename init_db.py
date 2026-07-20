import sqlite3

connection = sqlite3.connect('database.db')


cursor = connection.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        amount REAL NOT NULL
    )
''')


connection.commit()
connection.close()

print("Database initialized successfully! created table 'expenses'.")