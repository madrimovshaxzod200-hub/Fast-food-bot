from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from keyboards import menu_keyboard
from db import cursor, conn, get_products, add_order, get_card
from config import ADMIN_IDS


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum 😊",
        reply_markup=menu_keyboard
    )


# ===== MENU =====
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Menyu tanlang 👇",
        reply_markup=menu_keyboard
    )


# ===== Barcha mahsulotlarni ko‘rsatish =====
async def show_all_products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    products = get_products()

    if not products:
        await update.message.reply_text("Mahsulotlar yo‘q")
        return

    keyboard = [[p[1]] for p in products]
    keyboard.append(["🛒 Savat"])

    await update.message.reply_text(
        "🍔 Buyurtma menyusi:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ===== Kategoriya menyu =====
async def open_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🍔 Yegulik", "🥤 Ichimlik"]]

    await update.message.reply_text(
        "Kategoriya tanlang",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ===== Kategoriya orqali mahsulotlar =====
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🍔 Yegulik":
        products = get_products("food")

    elif text == "🥤 Ichimlik":
        products = get_products("drink")

    else:
        return

    if not products:
        await update.message.reply_text("Mahsulot yo‘q")
        return

    keyboard = [[p[1]] for p in products]
    keyboard.append(["🛒 Savat"])

    await update.message.reply_text(
        "Mahsulot tanlang 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ===== ADMIN mahsulot qo‘shish =====
async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🍔 Yegulik":
        category = "food"
    else:
        category = "drink"

    cursor.execute(
        "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
        (
            context.user_data["name"],
            context.user_data["price"],
            category
        )
    )

    conn.commit()

    await update.message.reply_text("✅ Mahsulot qo‘shildi")

    return -1


# ===== Savatga qo‘shish =====
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "cart" not in context.user_data:
        context.user_data["cart"] = []

    context.user_data["cart"].append(text)

    await update.message.reply_text(f"{text} savatga qo'shildi ✅")


# ===== Savatni ko‘rish =====
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])

    if not cart:
        await update.message.reply_text("Savat bo'sh ❌")
        return

    text = "🛒 Savat:\n\n"
    for item in cart:
        text += f"• {item}\n"

    keyboard = [["✅ Buyurtma berish"]]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ===== Buyurtma berish =====
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])

    if not cart:
        await update.message.reply_text("Savat bo'sh")
        return

    user_id = update.effective_user.id
    items = ", ".join(cart)

    total_price = 0

    add_order(user_id, items, total_price)

    card = get_card()

    await update.message.reply_text(
        f"💳 To'lov uchun karta:\n\n{card}\n\n"
        "📸 Chek rasmini yuboring"
    )

    context.user_data["waiting_check"] = True


# ===== Chek qabul qilish =====
async def receive_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_check"):
        return

    photo = update.message.photo[-1].file_id
    user = update.effective_user

    for admin in ADMIN_IDS:
        await context.bot.send_photo(
            admin,
            photo=photo,
            caption=f"🧾 Yangi buyurtma\n\nUser: {user.id}"
        )

    await update.message.reply_text("Buyurtma yuborildi ✅")

    context.user_data["cart"] = []
    context.user_data["waiting_check"] = False

async def category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return


