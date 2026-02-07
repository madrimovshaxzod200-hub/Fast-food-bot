from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from config import ADMIN_IDS
from db import add_product
from states import NAME, PRICE, CATEGORY

# ===== ADMIN PANEL =====
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    keyboard = [
        ["➕ Mahsulot qo'shish"],
        ["❌ Mahsulot o'chirish"],
        ["✏️ Mahsulot tahrirlash"],
        ["💳 Karta sozlash"],
        ["📦 Buyurtmalar"]
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
    await update.message.reply_text("Narxini kiriting:")
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
    category_text = update.message.text

    if "Yegulik" in category_text:
        category = "food"
    else:
        category = "drink"

    add_product(
        context.user_data["name"],
        context.user_data["price"],
        category
    )

    await update.message.reply_text("✅ Mahsulot qo'shildi")
    return ConversationHandler.END
