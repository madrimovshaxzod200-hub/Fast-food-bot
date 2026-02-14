from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart,Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import asyncio
import sqlite3
import datetime
import os
TOKEN = "7782621732:AAGxkKO8fYw8sGqYcENJIpZ5punZwhA1scU"

bot = Bot(token=TOKEN)
dp = Dispatcher()



# ================= START MENYU =================

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Zal"), KeyboardButton(text="🛵 Delivery")],
        [KeyboardButton(text="📦 Buyurtmalarim")]
    ],
    resize_keyboard=True
)


# ================= CATEGORY MENYU =================

category_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍔 Yegulik"), KeyboardButton(text="🥤 Ichimlik")],
        [KeyboardButton(text="🛒 Savat")],
        [KeyboardButton(text="⬅ Orqaga")]
    ],
    resize_keyboard=True
)

import sqlite3

conn = sqlite3.connect("fastfood.db")
cursor = conn.cursor()

# ================= USERS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    phone TEXT
)
""")

# ================= PRODUCTS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER,
    category TEXT
)
""")

# ================= CART =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER
)
""")

# ================= ORDERS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_type TEXT,
    table_number INTEGER,
    phone TEXT,
    status TEXT,
    payment TEXT,
    total INTEGER,
    created_at TEXT
)
""")

# ================= ORDER ITEMS =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    price INTEGER
)
""")

conn.commit()
conn.close()

# ================= FSM =================

class OrderState(StatesGroup):
    order_type = State()
    table_number = State()
    phone = State()


# ================= /START =================

@dp.message(CommandStart())
async def start_handler(message: types.Message):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id)
    VALUES (?)
    """, (message.from_user.id,))

    conn.commit()
    conn.close()

    await message.answer(
        "🍟 FastFood botiga xush kelibsiz!",
        reply_markup=start_menu
    )


# ================= ZAL BUYURTMA =================

@dp.message(F.text == "🏠 Zal")
async def zal_order(message: types.Message, state: FSMContext):

    await state.update_data(order_type="zal")

    await message.answer("🪑 Stol raqamini kiriting:")
    await state.set_state(OrderState.table_number)


@dp.message(OrderState.table_number)
async def save_table(message: types.Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("❗ Stol raqami faqat son bo‘lishi kerak")
        return

    await state.update_data(table_number=int(message.text))

    await message.answer(
        "✅ Stol qabul qilindi",
        reply_markup=category_menu
    )

    await state.clear()


# ================= DELIVERY BUYURTMA =================

@dp.message(F.text == "🛵 Delivery")
async def delivery_order(message: types.Message, state: FSMContext):

    await state.update_data(order_type="delivery")

    await message.answer("📞 Telefon raqamingizni kiriting:")
    await state.set_state(OrderState.phone)


@dp.message(OrderState.phone)
async def save_phone(message: types.Message, state: FSMContext):

    phone = message.text

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET phone=?
    WHERE user_id=?
    """, (phone, message.from_user.id))

    conn.commit()
    conn.close()

    await message.answer(
        "✅ Telefon saqlandi",
        reply_markup=category_menu
    )

    await state.clear()


# ================= ORQAGA =================

@dp.message(F.text == "⬅ Orqaga")
async def back_menu(message: types.Message):
    await message.answer("🏠 Asosiy menyu", reply_markup=start_menu)

# ================= MAHSULOTLARNI CHIQARISH =================

async def show_products(message: types.Message, category: str, title: str):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM products WHERE category=?",
        (category,)
    )

    products = cursor.fetchall()
    conn.close()

    if not products:
        await message.answer("❌ Mahsulotlar mavjud emas")
        return

    keyboard = []

    for p in products:
        keyboard.append([KeyboardButton(text=p[0])])

    keyboard.append([KeyboardButton(text="⬅ Orqaga")])

    markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    await message.answer(title, reply_markup=markup)


# ================= YEGULIK =================

@dp.message(F.text == "🍔 Yegulik")
async def food_products(message: types.Message):
    await show_products(message, "food", "🍔 Yeguliklar:")


# ================= ICHIMLIK =================

@dp.message(F.text == "🥤 Ichimlik")
async def drink_products(message: types.Message):
    await show_products(message, "drink", "🥤 Ichimliklar:")


# ================= SAVATGA QO‘SHISH =================

@dp.message()
async def add_product_to_cart(message: types.Message):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM products WHERE name=?",
        (message.text,)
    )

    product = cursor.fetchone()

    if not product:
        conn.close()
        return

    product_id = product[0]

    cursor.execute("""
        SELECT id, quantity
        FROM cart
        WHERE user_id=? AND product_id=?
    """, (message.from_user.id, product_id))

    item = cursor.fetchone()

    if item:
        cursor.execute("""
            UPDATE cart
            SET quantity = quantity + 1
            WHERE id=?
        """, (item[0],))
    else:
        cursor.execute("""
            INSERT INTO cart(user_id, product_id, quantity)
            VALUES (?, ?, 1)
        """, (message.from_user.id, product_id))

    conn.commit()
    conn.close()

    await message.answer("✅ Savatga qo‘shildi")

# ================= SAVATNI CHIQARISH =================

async def show_cart(message: types.Message):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cart.product_id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON products.id = cart.product_id
        WHERE cart.user_id=?
    """, (message.from_user.id,))

    items = cursor.fetchall()

    if not items:
        await message.answer("🛒 Savat bo‘sh")
        conn.close()
        return

    text = "🛒 Sizning savatingiz:\n\n"
    total = 0

    keyboard = []

    for product_id, name, price, qty in items:

        summa = price * qty
        total += summa

        text += f"{name} x{qty} — {summa:,} so‘m\n"

        keyboard.append([
            KeyboardButton(text=f"➕ {name}"),
            KeyboardButton(text=f"➖ {name}")
        ])

    text += f"\n💰 Jami: {total:,} so‘m"

    keyboard.append([KeyboardButton(text="🗑 Savatni tozalash")])
    keyboard.append([KeyboardButton(text="✅ Buyurtma berish")])
    keyboard.append([KeyboardButton(text="⬅ Orqaga")])

    markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

    await message.answer(text, reply_markup=markup)

    conn.close()


# ================= SAVATNI OCHISH =================

@dp.message(F.text == "🛒 Savat")
async def open_cart(message: types.Message):
    await show_cart(message)


# ================= PLUS =================

@dp.message(F.text.startswith("➕ "))
async def plus_product(message: types.Message):

    name = message.text.replace("➕ ", "")

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products WHERE name=?", (name,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        return

    cursor.execute("""
        UPDATE cart
        SET quantity = quantity + 1
        WHERE user_id=? AND product_id=?
    """, (message.from_user.id, product[0]))

    conn.commit()
    conn.close()

    await show_cart(message)


# ================= MINUS =================

@dp.message(F.text.startswith("➖ "))
async def minus_product(message: types.Message):

    name = message.text.replace("➖ ", "")

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products WHERE name=?", (name,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        return

    cursor.execute("""
        SELECT id, quantity
        FROM cart
        WHERE user_id=? AND product_id=?
    """, (message.from_user.id, product[0]))

    item = cursor.fetchone()

    if item:
        if item[1] <= 1:
            cursor.execute("DELETE FROM cart WHERE id=?", (item[0],))
        else:
            cursor.execute("""
                UPDATE cart
                SET quantity = quantity - 1
                WHERE id=?
            """, (item[0],))

    conn.commit()
    conn.close()

    await show_cart(message)


# ================= SAVATNI TOZALASH =================

@dp.message(F.text == "🗑 Savatni tozalash")
async def clear_cart(message: types.Message):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM cart WHERE user_id=?",
        (message.from_user.id,)
    )

    conn.commit()
    conn.close()

    await message.answer("🧹 Savat tozalandi")

# ================= BUYURTMA TASDIQLASH MENYUSI =================

confirm_order_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Tasdiqlash")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ],
    resize_keyboard=True
)

payment_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💵 Naqd")],
        [KeyboardButton(text="💳 Karta")]
    ],
    resize_keyboard=True
)


# ================= BUYURTMA BERISH BOSHLASH =================

@dp.message(F.text == "✅ Buyurtma berish")
async def create_order(message: types.Message, state: FSMContext):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cart.product_id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON products.id = cart.product_id
        WHERE cart.user_id=?
    """, (message.from_user.id,))

    items = cursor.fetchall()

    if not items:
        await message.answer("🛒 Savat bo‘sh")
        conn.close()
        return

    text = "📦 Buyurtma:\n\n"
    total = 0

    order_text = ""

    for product_id, name, price, qty in items:
        summa = price * qty
        total += summa
        text += f"{name} x{qty}\n"
        order_text += f"{name} x{qty}\n"

    text += f"\n💰 {total:,} so‘m\n\nTasdiqlaysizmi?"

    await state.update_data(
        order_items=order_text,
        order_total=total
    )

    await message.answer(text, reply_markup=confirm_order_menu)

    conn.close()


# ================= BUYURTMANI TASDIQLASH =================

@dp.message(F.text == "✅ Tasdiqlash")
async def confirm_order(message: types.Message, state: FSMContext):

    data = await state.get_data()

    if "order_items" not in data:
        return

    await message.answer(
        "💳 To‘lov turini tanlang:",
        reply_markup=payment_menu
    )


# ================= BUYURTMANI BEKOR =================

@dp.message(F.text == "❌ Bekor qilish")
async def cancel_order(message: types.Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "❌ Buyurtma bekor qilindi",
        reply_markup=main_menu
    )


# ================= TO‘LOV TANLANGANDA ORDER SAQLASH =================

@dp.message(F.text.in_(["💵 Naqd", "💳 Karta"]))
async def save_order(message: types.Message, state: FSMContext):

    payment = message.text.replace("💵 ", "").replace("💳 ", "")

    data = await state.get_data()

    items = data["order_items"]
    total = data["order_total"]

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    # Order ID yaratish
    cursor.execute("SELECT MAX(id) FROM orders")
    last = cursor.fetchone()[0]
    order_id = 1 if last is None else last + 1

    # Order saqlash
    cursor.execute("""
        INSERT INTO orders (
            id,
            user_id,
            items,
            total,
            payment,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        order_id,
        message.from_user.id,
        items,
        total,
        payment,
        "yangi"
    ))

    # Savatni tozalash
    cursor.execute(
        "DELETE FROM cart WHERE user_id=?",
        (message.from_user.id,)
    )

    conn.commit()
    conn.close()

    await message.answer(
        f"✅ Buyurtma qabul qilindi!\n📦 Buyurtma ID: {order_id}",
        reply_markup=main_menu
    )

    await state.clear()

# ================= ADMIN SOZLAMALAR =================

ADMIN_ID = 6780565815  # 🔥 BU YERGA O'Z TELEGRAM IDINGNI YOZ

from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Siz admin emassiz ❌")
        return

    await message.answer(
        "🔐 Admin panelga xush kelibsiz",
        reply_markup=admin_menu
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Faol buyurtmalar")],
        [KeyboardButton(text="🔍 Buyurtma qidirish")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)

admin_order_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Tasdiqlash")],
        [KeyboardButton(text="🍳 Tayyor")],
        [KeyboardButton(text="🚚 Yetkazildi")],
        [KeyboardButton(text="❌ Bekor")]
    ],
    resize_keyboard=True
)

# ================= ADMIN KIRISH =================

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "👨‍💼 Admin panel",
        reply_markup=admin_menu
    )

# ================= FAOL BUYURTMALAR =================

@dp.message(F.text == "📦 Faol buyurtmalar")
async def active_orders(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, items, total, payment, status
        FROM orders
        WHERE status != 'yetkazildi' AND status != 'bekor'
        ORDER BY id ASC
    """)

    orders = cursor.fetchall()
    conn.close()

    if not orders:
        await message.answer("Faol buyurtmalar yo‘q")
        return

    for order in orders:

        order_id, user_id, items, total, payment, status = order

        text = (
            f"📦 Buyurtma #{order_id}\n\n"
            f"{items}\n"
            f"💰 {total:,} so‘m\n"
            f"💳 {payment}\n"
            f"📊 Status: {status}"
        )

        await state.update_data(
            admin_order_id=order_id,
            admin_user_id=user_id
        )

        await message.answer(text, reply_markup=admin_order_menu)

# ================= ADMIN ACTION =================

@dp.message(F.text.in_(["✅ Tasdiqlash", "🍳 Tayyor", "🚚 Yetkazildi", "❌ Bekor"]))
async def admin_order_action(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    action_map = {
        "✅ Tasdiqlash": "tasdiqlandi",
        "🍳 Tayyor": "tayyor",
        "🚚 Yetkazildi": "yetkazildi",
        "❌ Bekor": "bekor"
    }

    status = action_map[message.text]

    data = await state.get_data()
    order_id = data.get("admin_order_id")
    user_id = data.get("admin_user_id")

    if not order_id:
        return

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE orders SET status=? WHERE id=?",
        (status, order_id)
    )

    conn.commit()
    conn.close()

    msg_map = {
        "tasdiqlandi": "✅ Buyurtmangiz tasdiqlandi",
        "tayyor": "🍳 Buyurtmangiz tayyor bo‘ldi",
        "yetkazildi": "🚚 Buyurtma yetkazildi",
        "bekor": "❌ Buyurtma bekor qilindi"
    }

    try:
        await bot.send_message(
            user_id,
            f"{msg_map[status]}\n📦 Buyurtma #{order_id}"
        )
    except:
        pass

    await message.answer("✅ Status yangilandi")
    await state.clear()

# ================= BUYURTMA QIDIRISH =================

class SearchOrder(StatesGroup):
    order_id = State()


@dp.message(F.text == "🔍 Buyurtma qidirish")
async def search_order_start(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("Order ID kiriting:")
    await state.set_state(SearchOrder.order_id)


@dp.message(SearchOrder.order_id)
async def search_order_result(message: types.Message, state: FSMContext):

    if not message.text.isdigit():
        return

    order_id = int(message.text)

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, items, total, payment, status
        FROM orders
        WHERE id=?
    """, (order_id,))

    order = cursor.fetchone()
    conn.close()

    if not order:
        await message.answer("Buyurtma topilmadi")
        return

    oid, user_id, items, total, payment, status = order

    text = (
        f"📦 Buyurtma #{oid}\n\n"
        f"{items}\n"
        f"💰 {total:,} so‘m\n"
        f"💳 {payment}\n"
        f"📊 Status: {status}"
    )

    await state.update_data(
        admin_order_id=oid,
        admin_user_id=user_id
    )

    await message.answer(text, reply_markup=admin_order_menu)
    await state.clear()

# ================= ADMIN ORTGA =================

@dp.message(F.text == "⬅️ Ortga")
async def admin_back(message: types.Message):

    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin panel", reply_markup=admin_menu)
    else:
        await message.answer("Bosh menyu", reply_markup=main_menu)

# ================= ADMIN MAHSULOT MENYUSI =================

admin_product_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Mahsulot qo‘shish")],
        [KeyboardButton(text="✏️ Narx o‘zgartirish")],
        [KeyboardButton(text="❌ Mahsulot o‘chirish")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)

# Admin menyuga mahsulot tugmasi qo‘shish
admin_menu.keyboard.insert(1, [KeyboardButton(text="🍔 Mahsulotlar")])


@dp.message(F.text == "🍔 Mahsulotlar")
async def admin_products(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "Mahsulot boshqaruvi",
        reply_markup=admin_product_menu
)

# ================= MAHSULOT QO‘SHISH =================

class AddProduct(StatesGroup):
    name = State()
    price = State()
    category = State()


@dp.message(F.text == "➕ Mahsulot qo‘shish")
async def add_product_start(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("Mahsulot nomini yozing:")
    await state.set_state(AddProduct.name)


@dp.message(AddProduct.name)
async def add_product_name(message: types.Message, state: FSMContext):

    await state.update_data(name=message.text)
    await message.answer("Narxini kiriting:")
    await state.set_state(AddProduct.price)


@dp.message(AddProduct.price)
async def add_product_price(message: types.Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("Faqat son kiriting")
        return

    await state.update_data(price=int(message.text))

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍔 Yegulik")],
            [KeyboardButton(text="🥤 Ichimlik")]
        ],
        resize_keyboard=True
    )

    await message.answer("Kategoriya tanlang:", reply_markup=kb)
    await state.set_state(AddProduct.category)


@dp.message(AddProduct.category)
async def add_product_finish(message: types.Message, state: FSMContext):

    data = await state.get_data()

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, price, category)
        VALUES (?, ?, ?)
    """, (
        data["name"],
        data["price"],
        message.text
    ))

    conn.commit()
    conn.close()

    await message.answer(
        "✅ Mahsulot qo‘shildi",
        reply_markup=admin_product_menu
    )

    await state.clear()

# ================= NARX O‘ZGARTIRISH =================

class EditPrice(StatesGroup):
    product = State()
    new_price = State()


@dp.message(F.text == "✏️ Narx o‘zgartirish")
async def edit_price_start(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM products")
    products = cursor.fetchall()

    conn.close()

    keyboard = [[KeyboardButton(text=p[0])] for p in products]

    await message.answer(
        "Mahsulot tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

    await state.set_state(EditPrice.product)


@dp.message(EditPrice.product)
async def edit_price_product(message: types.Message, state: FSMContext):

    await state.update_data(product=message.text)
    await message.answer("Yangi narx kiriting:")
    await state.set_state(EditPrice.new_price)


@dp.message(EditPrice.new_price)
async def edit_price_finish(message: types.Message, state: FSMContext):

    if not message.text.isdigit():
        return

    data = await state.get_data()

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET price=?
        WHERE name=?
    """, (int(message.text), data["product"]))

    conn.commit()
    conn.close()

    await message.answer(
        "✅ Narx yangilandi",
        reply_markup=admin_product_menu
    )

    await state.clear()


# ================= MAHSULOT O‘CHIRISH =================

class DeleteProduct(StatesGroup):
    product = State()


@dp.message(F.text == "❌ Mahsulot o‘chirish")
async def delete_product_start(message: types.Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM products")
    products = cursor.fetchall()

    conn.close()

    keyboard = [[KeyboardButton(text=p[0])] for p in products]

    await message.answer(
        "Qaysi mahsulotni o‘chiramiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

    await state.set_state(DeleteProduct.product)


@dp.message(DeleteProduct.product)
async def delete_product_finish(message: types.Message, state: FSMContext):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE name=?",
        (message.text,)
    )

    conn.commit()
    conn.close()

    await message.answer(
        "✅ Mahsulot o‘chirildi",
        reply_markup=admin_product_menu
    )

    await state.clear()

# ================= ADMIN STATISTIKA MENYUSI =================

admin_stat_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Bugungi statistika")],
        [KeyboardButton(text="📜 Buyurtma tarixi")],
        [KeyboardButton(text="🟢 Faol buyurtmalar")],
        [KeyboardButton(text="🔍 Order qidirish")],
        [KeyboardButton(text="⬅️ Ortga")]
    ],
    resize_keyboard=True
)

# Admin menyuga statistika qo‘shamiz
admin_menu.keyboard.append([KeyboardButton(text="📊 Statistika")])


@dp.message(F.text == "📊 Statistika")
async def admin_stat(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "Statistika menyusi",
        reply_markup=admin_stat_menu
)

# ================= BUGUNGI STATISTIKA =================

@dp.message(F.text == "📊 Bugungi statistika")
async def today_statistics(message: types.Message):

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*), SUM(total)
        FROM orders
        WHERE date=? AND status!='Bekor'
    """, (today,))

    order_count, total_sum = cursor.fetchone()

    cursor.execute("""
        SELECT SUM(total)
        FROM orders
        WHERE payment='Naqd' AND date=?
    """, (today,))
    cash = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(total)
        FROM orders
        WHERE payment='Karta' AND date=?
    """, (today,))
    card = cursor.fetchone()[0] or 0

    conn.close()

    text = (
        "📊 Bugungi statistika\n\n"
        f"📦 Buyurtmalar soni: {order_count or 0}\n"
        f"💰 Jami daromad: {total_sum or 0:,}\n\n"
        f"💵 Naqd: {cash:,}\n"
        f"💳 Karta: {card:,}"
    )

    await message.answer(text)

# ================= FAOL BUYURTMALAR =================

@dp.message(F.text == "🟢 Faol buyurtmalar")
async def active_orders(message: types.Message):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, order_type, location, total
        FROM orders
        WHERE status IN ('Yangi', 'Tasdiqlandi', 'Tayyor')
        ORDER BY id DESC
    """)

    orders = cursor.fetchall()
    conn.close()

    if not orders:
        await message.answer("Faol buyurtmalar yo‘q")
        return

    text = "🟢 Faol buyurtmalar\n\n"

    for o in orders:
        text += (
            f"📦 #{o[0]}\n"
            f"{o[1]}: {o[2]}\n"
            f"💰 {o[3]:,}\n\n"
        )

    await message.answer(text)

# ================= BUYURTMA TARIXI =================

@dp.message(F.text == "📜 Buyurtma tarixi")
async def order_history(message: types.Message):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, total, status
        FROM orders
        ORDER BY id DESC
        LIMIT 15
    """)

    orders = cursor.fetchall()
    conn.close()

    if not orders:
        await message.answer("Tarix bo‘sh")
        return

    text = "📜 Oxirgi buyurtmalar\n\n"

    for o in orders:
        text += (
            f"📦 #{o[0]}\n"
            f"📅 {o[1]}\n"
            f"💰 {o[2]:,}\n"
            f"📌 {o[3]}\n\n"
        )

    await message.answer(text)

# ================= ORDER QIDIRISH =================

class SearchOrder(StatesGroup):
    order_id = State()


@dp.message(F.text == "🔍 Order qidirish")
async def search_order_start(message: types.Message, state: FSMContext):
    await message.answer("Order ID kiriting:")
    await state.set_state(SearchOrder.order_id)


@dp.message(SearchOrder.order_id)
async def search_order_finish(message: types.Message, state: FSMContext):

    if not message.text.isdigit():
        return

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT order_type, location, total, status
        FROM orders
        WHERE id=?
    """, (int(message.text),))

    order = cursor.fetchone()
    conn.close()

    if not order:
        await message.answer("Topilmadi")
        await state.clear()
        return

    text = (
        f"📦 #{message.text}\n"
        f"{order[0]}: {order[1]}\n"
        f"💰 {order[2]:,}\n"
        f"📌 {order[3]}"
    )

    await message.answer(text)
    await state.clear()

# ================= ORDER STATUS YANGILASH =================

async def update_order_status(order_id, status):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status=?
        WHERE id=?
    """, (status, order_id))

    cursor.execute("""
        SELECT user_id FROM orders WHERE id=?
    """, (order_id,))

    user = cursor.fetchone()
    conn.commit()
    conn.close()

    if not user:
        return

    user_id = user[0]

    status_text = {
        "Tasdiqlandi": "✅ Buyurtmangiz tasdiqlandi",
        "Tayyor": "🍳 Buyurtmangiz tayyor",
        "Yetkazildi": "🚚 Buyurtma yetkazildi",
        "Bekor": "❌ Buyurtma bekor qilindi"
    }

    if status in status_text:
        try:
            await bot.send_message(
                user_id,
                f"{status_text[status]}\n📦 Buyurtma #{order_id}"
            )
        except:
            pass

# ================= ADMIN ORDER ACTION =================

@dp.callback_query(F.data.startswith("admin_order"))
async def admin_order_action(callback: types.CallbackQuery):

    _, action, order_id = callback.data.split("_")
    order_id = int(order_id)

    if action == "accept":
        await update_order_status(order_id, "Tasdiqlandi")

    elif action == "ready":
        await update_order_status(order_id, "Tayyor")

    elif action == "deliver":
        await update_order_status(order_id, "Yetkazildi")

    elif action == "cancel":
        await update_order_status(order_id, "Bekor")

    await callback.answer("Yangilandi")

async def clear_cart(user_id):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM cart WHERE user_id=?
    """, (user_id,))

    conn.commit()
    conn.close()
    await clear_cart(message.from_user.id)

async def create_order(user_id, order_type, location, payment):

    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT product_name, quantity, price
        FROM cart
        WHERE user_id=?
    """, (user_id,))

    cart_items = cursor.fetchall()

    if not cart_items:
        return None

    total = sum(item[1] * item[2] for item in cart_items)

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO orders (user_id, order_type, location, payment, total, status, date)
        VALUES (?, ?, ?, ?, ?, 'Yangi', ?)
    """, (user_id, order_type, location, payment, total, date))

    order_id = cursor.lastrowid

    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_items
            (order_id, product_name, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item[0], item[1], item[2]))

    conn.commit()
    conn.close()

    await clear_cart(user_id)

    return order_id, total

async def notify_admin(order_id, order_type, location, payment, total):

    text = (
        f"🆕 Buyurtma #{order_id}\n\n"
        f"{order_type}: {location}\n"
        f"💳 To‘lov: {payment}\n"
        f"💰 {total:,}"
    )

    await bot.send_message(ADMIN_ID, text)

# ================= BOT ISHGA TUSHIRISH =================

async def create_tables():
    conn = sqlite3.connect("fastfood.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        full_name TEXT,
        phone TEXT,
        table_number INTEGER,
        products TEXT,
        total_price INTEGER,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

async def main():
    await create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
