from telegram import ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    [
        ["🏠 Zal", "🛵 Delivery"],
        ["📦 Buyurtmalarim"]
    ],
    resize_keyboard=True
)

menu_keyboard = ReplyKeyboardMarkup(
    [
        ["🍔 Yegulik", "🥤 Ichimlik"],
        ["🛒 Savat"],
        ["⬅ Orqaga"]
    ],
    resize_keyboard=True
)
