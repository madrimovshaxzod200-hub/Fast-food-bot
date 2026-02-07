import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()


def create_tables():
    # Products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        category TEXT
    )
    """)

    # Orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        status TEXT
    )
    """)

    # Order items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_name TEXT,
        quantity INTEGER,
        price INTEGER
    )
    """)

    # Settings (karta raqam uchun)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        card TEXT
    )
    """)

    conn.commit()


def add_product(name, price, category):
    cursor.execute(
        "INSERT INTO products(name, price, category) VALUES(?,?,?)",
        (name, price, category)
    )
    conn.commit()


def get_products(category):
    cursor.execute(
        "SELECT name, price FROM products WHERE category=?",
        (category,)
    )
    return cursor.fetchall()


def update_card(card):
    cursor.execute("DELETE FROM settings")
    cursor.execute("INSERT INTO settings(id, card) VALUES(1,?)", (card,))
    conn.commit()


def get_card():
    cursor.execute("SELECT card FROM settings WHERE id=1")
    result = cursor.fetchone()
    return result[0] if result else None


create_tables()
