from telegram import ReplyKeyboardMarkup

def start_menu():
    return ReplyKeyboardMarkup([
        ["🏠 Zal", "🛵 Dastavka "],
        ["📦 Buyurtmalarim"]
    ], resize_keyboard=True)
