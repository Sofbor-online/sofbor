import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import Dispatcher

# Ініціалізація Flask
app = Flask(__name__)

# Отримуємо змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Створюємо додаток для Telegram бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши або надішли файл, і адміністратор отримає його.")

async def forward_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = f"📩 Повідомлення від @{user.username or user.first_name} (ID: {user.id}):\n\n{update.message.text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

async def forward_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = update.message.caption or ""
    file_info = f"📎 Файл від @{user.username or user.first_name} (ID: {user.id})"
    
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await file.download_to_drive("photo.jpg")
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=open("photo.jpg", "rb"), caption=caption or file_info)
    elif update.message.document:
        file = await update.message.document.get_file()
        await file.download_to_drive("document")
        await context.bot.send_document(chat_id=ADMIN_ID, document=open("document", "rb"), caption=caption or file_info)
    elif update.message.video:
        file = await update.message.video.get_file()
        await file.download_to_drive("video.mp4")
        await context.bot.send_video(chat_id=ADMIN_ID, video=open("video.mp4", "rb"), caption=caption or file_info)
    else:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"{file_info} (тип не підтримується)")

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return
    if context.args and len(context.args) >= 2:
        user_id = int(context.args[0])
        reply_text = ' '.join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"💬 Від адміністратора:\n{reply_text}")
    else:
        await update.message.reply_text("❗ Формат: /reply <user_id> <повідомлення>")

# Ініціалізація бота
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_to_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_text))
    app.add_handler(MessageHandler(filters.PHOTO | filters.DOCUMENT | filters.VIDEO, forward_media))
    return app

# Створюємо веб-сервер
@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = Update.de_json(json_str, bot)
    dispatcher.process_update(update)
    return "OK"

if __name__ == "__main__":
    from telegram.ext import Dispatcher
    import logging
    
    # Логування
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    
    # Ініціалізація бота та диспетчера
    bot = ApplicationBuilder().token(BOT_TOKEN).build()
    dispatcher = Dispatcher(bot, None)
    
    # Запуск сервера
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
