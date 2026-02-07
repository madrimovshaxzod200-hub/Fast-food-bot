from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_categories, get_products

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [["📋 Menyu"]]

    await update.message.reply_text(
        "Xush kelibsiz 🍔",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    categories = get_categories()

    keyboard = [[c[0]] for c in categories]

    await update.message.reply_text(
        "Kategoriya tanlang",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    category = update.message.text
    products = get_products(category)

    text = f"{category}\n\n"

    for name, price in products:
        text += f"{name} - {price} so‘m\n"

    await update.message.reply_text(text)
