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
from handlers.admin import (
    admin_panel,
    add_product_start,
    get_name,
    get_price,
    get_category
)

from handlers.client import add_to_cart, show_cart, checkout, receive_check

app = Application.builder().token(TOKEN).build()


# ===== Conversation (Mahsulot qo‘shish) =====
from handlers.admin import *

app.add_handler(MessageHandler(filters.Regex("🛒 Savat"), show_cart))
app.add_handler(MessageHandler(filters.Regex("✅ Buyurtma berish"), checkout))
app.add_handler(MessageHandler(filters.PHOTO, receive_check))

conv_add = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("➕ Mahsulot qo'shish"), add_product_start)],
    states={
        NAME: [MessageHandler(filters.TEXT, get_name)],
        PRICE: [MessageHandler(filters.TEXT, get_price)],
        CATEGORY: [MessageHandler(filters.TEXT, get_category)],
    },
    fallbacks=[]
)

conv_delete = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("❌ Mahsulot o'chirish"), delete_product_start)],
    states={
        DELETE_NAME: [MessageHandler(filters.TEXT, delete_product_finish)]
    },
    fallbacks=[]
)

conv_card = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("💳 Karta sozlash"), card_start)],
    states={
        CARD_NUMBER: [MessageHandler(filters.TEXT, card_finish)]
    },
    fallbacks=[]
)

app.add_handler(conv_add)
app.add_handler(conv_delete)
app.add_handler(conv_card)

app.add_handler(MessageHandler(filters.Text("📦 Buyurtmalar"), show_orders))

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

conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("➕ Mahsulot qo'shish"), add_product_start)],
    states={
        NAME: [MessageHandler(filters.TEXT, get_name)],
        PRICE: [MessageHandler(filters.TEXT, get_price)],
        CATEGORY: [MessageHandler(filters.TEXT, get_category)],
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
