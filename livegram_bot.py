import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши щось, і адміністратор отримає твоє повідомлення.")

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    msg = f"📩 Повідомлення від @{user.username or user.first_name} (ID: {user.id}):\n\n{update.message.text}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return
    if context.args and len(context.args) >= 2:
        user_id = int(context.args[0])
        reply_text = ' '.join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"💬 Від адміністратора:\n{reply_text}")
    else:
        await update.message.reply_text("❗ Формат: /reply <user_id> <повідомлення>")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reply", reply_to_user))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
app.run_polling()
