from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    await update.message.reply_text(
        "Admin panel 👨‍💻"
    )
