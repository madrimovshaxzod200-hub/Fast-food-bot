from telegram import Update
from telegram.ext import ContextTypes
from keyboards import start_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xush kelibsiz 🍔",
        reply_markup=start_menu()
    )
