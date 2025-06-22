import sqlite3

# Connect to the database file (it will be created if it doesn't exist)
connection = sqlite3.connect('database.db')

# Open the schema file and execute the SQL commands
with open('schema.sql') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()

print("Database initialized successfully.")