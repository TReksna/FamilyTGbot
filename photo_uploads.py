import json
import os
from telegram import Update
from telegram.ext import ContextTypes
from sheets_integration import upload_file_to_drive
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Load messages from JSON file
with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)

PHOTO_PROMPT, PHOTO_NAME = range(2)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"Photos/{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(photo_path)

    await update.message.reply_text(messages['photo_prompt'])
    context.user_data['photo_path'] = photo_path

    return PHOTO_NAME

async def handle_photo_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo_name = update.message.text
    photo_path = context.user_data.get('photo_path')

    if photo_path:
        file_id = upload_file_to_drive(photo_path, photo_name)
        await update.message.reply_text(messages['photo_uploaded_success'].replace("{name}", photo_name).replace("{link}", f'https://drive.google.com/file/d/{file_id}/view'))
        os.remove(photo_path)
    else:
        await update.message.reply_text("Photo path not found. Please try again.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(messages['cancel_message'])
    return ConversationHandler.END
