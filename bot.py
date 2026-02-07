from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

from config import TOKEN
from handlers.admin import admin_panel, add_product_start, get_name, get_price
from handlers.client import *
from keyboards import main_menu
from states import *
import db

app = Application.builder().token(TOKEN).build()


# ===== Conversation (Mahsulot qo‘shish) =====
conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Text("+ Mahsulot qo‘shish"), add_product_start)
    ],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
    },
    fallbacks=[]
)


# ===== START =====
app.add_handler(CommandHandler("start", start))


# ===== ADMIN PANEL =====
app.add_handler(CommandHandler("admin", admin_panel))


# ===== Conversation handler =====
app.add_handler(conv)


# ===== CLIENT MENYU =====
app.add_handler(MessageHandler(filters.Text("📋 Menu"), menu))
app.add_handler(MessageHandler(filters.TEXT, category_products))


# ===== Zal / Delivery =====
app.add_handler(
    MessageHandler(filters.Text(["🏠 Zal", "🚚 Delivery"]), open_menu)
)


# ===== Mahsulot ko‘rsatish =====
app.add_handler(
    MessageHandler(filters.Text(["🍔 Yegulik", "🥤 Ichimlik"]), show_products)
)


# ===== RUN =====
app.run_polling()
