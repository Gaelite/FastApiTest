import sqlite3

con = sqlite3.connect("fastApi.db")
cur = con.cursor()

# Create tables
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER,
    data TEXT,
    FOREIGN KEY (userId) REFERENCES users(id)
)
""")

con.commit()
con.close()