import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        category TEXT
    )
    """)

    conn.commit()

def add_product(name, price, category):
    cursor.execute(
        "INSERT INTO products(name, price, category) VALUES(?,?,?)",
        (name, price, category)
    )
    conn.commit()

def get_categories():
    cursor.execute("SELECT DISTINCT category FROM products")
    return cursor.fetchall()

def get_products(category):
    cursor.execute(
        "SELECT name, price FROM products WHERE category=?",
        (category,)
    )
    return cursor.fetchall()
