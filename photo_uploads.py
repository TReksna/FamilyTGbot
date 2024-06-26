import json
import os
from telegram import Update
from telegram.ext import ContextTypes
from sheets_integration import upload_file_to_drive

# Load messages from JSON file
with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"Photos/{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(photo_path)

    await update.message.reply_text(messages['photo_prompt'])
    context.user_data['photo_path'] = photo_path

async def handle_photo_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo_name = update.message.text
    photo_path = context.user_data.get('photo_path')

    file_id = upload_file_to_drive(photo_path, photo_name)
    await update.message.reply_text(messages['photo_uploaded_success'].replace("{name}", photo_name).replace("{link}", f'https://drive.google.com/file/d/{file_id}/view'))
    os.remove(photo_path)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(messages['cancel_message'])
