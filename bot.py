from telegram.ext import Application, CommandHandler
from config import TOKEN
from handlers.client import start
from handlers.admin import admin_panel
from db import init_db

init_db()

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin_panel))

app.run_polling()
