from db import cursor, conn

def get_products(category):
    cursor.execute("SELECT * FROM products WHERE category=?", (category,))
    return cursor.fetchall()
