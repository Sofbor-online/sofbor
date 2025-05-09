import os
from telegram import Update, File
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши або надішли файл, і адміністратор отримає його.")

# Переслати текст адміну
async def forward_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = f"📩 Повідомлення від @{user.username or user.first_name} (ID: {user.id}):\n\n{update.message.text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

# Переслати медіа адміну
async def forward_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = update.message.caption or ""
    file_info = f"📎 Файл від @{user.username or user.first_name} (ID: {user.id})"
    
    # Визначити тип медіа
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

# Відповідь адміну
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
