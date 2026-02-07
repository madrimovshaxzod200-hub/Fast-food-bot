from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from config import ADMIN_IDS
from db import add_product, delete_product, update_card, get_orders, get_products
from states import NAME, PRICE, CATEGORY, DELETE_NAME, CARD_NUMBER


# ===== ADMIN PANEL =====
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMIN_IDS:
        return

    keyboard = [
        ["➕ Mahsulot qo'shish", "❌ Mahsulot o'chirish"],
        ["💳 Karta sozlash", "📦 Buyurtmalar"]
    ]

    await update.message.reply_text(
        "👨‍💼 Admin panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ===== MAHSULOT QO'SHISH =====
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mahsulot nomini kiriting:")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Narx kiriting:")
    return PRICE


async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text

    keyboard = [["🍔 Yegulik", "🥤 Ichimlik"]]

    await update.message.reply_text(
        "Kategoriya tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CATEGORY


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):

    category = "food" if "Yegulik" in update.message.text else "drink"

    add_product(
        context.user_data["name"],
        context.user_data["price"],
        category
    )

    await update.message.reply_text("✅ Mahsulot qo'shildi")
    return ConversationHandler.END


# ===== MAHSULOT O'CHIRISH =====
async def delete_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    products = get_products()
    text = "O'chirish uchun nom yoz:\n\n"

    for p in products:
        text += f"{p[1]}\n"

    await update.message.reply_text(text)
    return DELETE_NAME


async def delete_product_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):

    delete_product(update.message.text)

    await update.message.reply_text("❌ Mahsulot o'chirildi")
    return ConversationHandler.END


# ===== KARTA SOZLASH =====
async def card_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yangi karta raqam kiriting:")
    return CARD_NUMBER


async def card_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):

    update_card(update.message.text)

    await update.message.reply_text("💳 Karta yangilandi")
    return ConversationHandler.END


# ===== BUYURTMALAR =====
async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    orders = get_orders()

    if not orders:
        await update.message.reply_text("Buyurtmalar yo'q")
        return

    text = "📦 Buyurtmalar:\n\n"

    for o in orders:
        text += f"{o}\n"

    await update.message.reply_text(text)
