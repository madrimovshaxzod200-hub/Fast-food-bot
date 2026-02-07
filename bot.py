from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import TOKEN
from handlers.admin import *
from handlers.client import *
from states import *
import db
from client import open_menu, show_products
from keyboards import main_menu



app = Application.builder().token(TOKEN).build()

# Admin conversation
conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("➕ Mahsulot qo‘shish"), add_product_start)],
    states={
        NAME: [MessageHandler(filters.TEXT, get_name)],
        PRICE: [MessageHandler(filters.TEXT, get_price)],
        CATEGORY: [MessageHandler(filters.TEXT, get_category)]
    },
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin_panel))

app.add_handler(conv)
app.add_handler(MessageHandler(filters.Text("📋 Menyu"), menu))
app.add_handler(MessageHandler(filters.TEXT, category_products))

app.add_handler(MessageHandler(filters.Text(["🏠 Zal","🛵 Delivery"]), open_menu))
app.add_handler(MessageHandler(filters.Text(["🍔 Yegulik","🥤 Ichimlik"]), show_products))

app.run_polling()
