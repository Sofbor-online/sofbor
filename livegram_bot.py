import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота і ID адміна
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Flask застосунок (для Render порту)
app = Flask(__name__)

# ====== Telegram Handlers ======

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли повідомлення або файл — адміністратор отримає його.")

# Пересилання тексту
async def forward_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = f"📩 Повідомлення від @{user.username or user.first_name} (ID: {user.id}):\n\n{update.message.text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text("✅ Дякуємо! Ваше повідомлення надіслано адміністратору.")

# Пересилання медіа
async def forward_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = update.message.caption or ""
    file_info = f"📎 Файл від @{user.username or user.first_name} (ID: {user.id})"

    if update.message.photo:
        photo = update.message.photo[-1]
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption or file_info)
    elif update.message.document:
        doc = update.message.document
        await context.bot.send_document(chat_id=ADMIN_ID, document=doc.file_id, caption=caption or file_info)
    elif update.message.video:
        video = update.message.video
        await context.bot.send_video(chat_id=ADMIN_ID, video=video.file_id, caption=caption or file_info)
    else:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"{file_info} (тип не підтримується)")

    await update.message.reply_text("✅ Дякуємо! Ваш файл надіслано адміністратору.")

# /reply <user_id> <повідомлення>
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return
    if context.args and len(context.args) >= 2:
        user_id = int(context.args[0])
        reply_text = ' '.join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"💬 Від адміністратора:\n{reply_text}")
    else:
        await update.message.reply_text("❗ Формат: /reply <user_id> <повідомлення>")

# ====== Запуск Telegram бота в іншому потоці ======
def start_bot():
    try:
        app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

        app_telegram.add_handler(CommandHandler("start", start))
        app_telegram.add_handler(CommandHandler("reply", reply_to_user))
        app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_text))
        app_telegram.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL | filters.VIDEO, forward_media))

        logger.info("🤖 Бот запущено (polling)...")
        app_telegram.run_polling()
    except Exception as e:
        logger.error(f"Error in bot: {e}")

# ====== Flask маршрут для Render порту ======
@app.route('/')
def home():
    return "Telegram bot is running!", 200

# ====== Запуск Flask та бота ======
if __name__ == '__main__':
    threading.Thread(target=start_bot).start()
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Flask server is running on port {port}")
    app.run(host='0.0.0.0', port=port)
