import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    category TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    status TEXT,
    total INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER
)
""")

conn.commit()

import sqlite3

def add_product(name, price, category):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, price, category)
        VALUES (?, ?, ?)
    """, (name, price, category))

    conn.commit()
    conn.close()

def delete_product(name):
    cursor.execute("DELETE FROM products WHERE name=?", (name,))
    conn.commit()


def update_card(card):
    cursor.execute("DELETE FROM settings")
    cursor.execute("INSERT INTO settings VALUES (?)", (card,))
    conn.commit()


def get_products():
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


def get_orders():
    cursor.execute("SELECT * FROM orders")
    return cursor.fetchall()
