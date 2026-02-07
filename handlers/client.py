from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from keyboards import menu_keyboard
from products import get_products
from db import cursor, conn


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


# ===== ZAL / DELIVERY =====
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

    msg = ""
    for p in products:
        msg += f"{p[1]} - {p[2]} so'm\n"

    await update.message.reply_text(msg)


# ===== category_products (bot.py talab qiladi) =====
async def category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# ===== ADMIN uchun category olish =====
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

from db import add_order, get_card
from telegram import ReplyKeyboardMarkup

# Savat
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "cart" not in context.user_data:
        context.user_data["cart"] = []

    context.user_data["cart"].append(text)

    await update.message.reply_text(f"{text} savatga qo'shildi ✅")
