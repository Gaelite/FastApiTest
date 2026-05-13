import sqlite3

# Conect with database 
con = sqlite3.connect("fastApi.db")
cur = con.cursor()

# Create example tables
cur.execute("CREATE TABLE users(id, username, password)")
cur.execute("CREATE TABLE info(id, userId, data)")
