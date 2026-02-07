from telegram import Update
from telegram.ext import ContextTypes
from keyboards import menu_keyboard
from products import get_products
from db import cursor, conn

async def open_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kategoriya tanlang", reply_markup=menu_keyboard)

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🍔 Yegulik":
        products = get_products("food")

    elif text == "🥤 Ichimlik":
        products = get_products("drink")

    else:
        return

    msg = ""
    for p in products:
        msg += f"{p[1]} - {p[2]} so'm\n"

    await update.message.reply_text(msg)
