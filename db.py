import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ================= PRODUCTS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    category TEXT
)
""")

# ================= SETTINGS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    card TEXT
)
""")

# ================= ORDERS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    items TEXT,
    total_price INTEGER,
    status TEXT
)
""")

conn.commit()

# -------- PRODUCTS --------

def add_product(name, price, category):
    cursor.execute(
        "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
        (name, price, category)
    )
    conn.commit()


def delete_product(name):
    cursor.execute("DELETE FROM products WHERE name=?", (name,))
    conn.commit()


def get_products(category):
    cursor.execute("SELECT name, price FROM products WHERE category=?", (category,))
    return cursor.fetchall()


# -------- CARD --------

def update_card(card):
    cursor.execute("DELETE FROM settings")
    cursor.execute("INSERT INTO settings (card) VALUES (?)", (card,))
    conn.commit()


def get_card():
    cursor.execute("SELECT card FROM settings LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result else "Kart kiritilmagan"


# -------- ORDERS --------

def add_order(user_id, items, total_price):
    cursor.execute(
        "INSERT INTO orders (user_id, items, total_price, status) VALUES (?, ?, ?, ?)",
        (user_id, items, total_price, "Kutilmoqda")
    )
    conn.commit()


def get_orders():
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    return cursor.fetchall()


def update_order_status(order_id, status):
    cursor.execute(
        "UPDATE orders SET status=? WHERE id=?",
        (status, order_id)
    )
    conn.commit()
