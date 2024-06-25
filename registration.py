import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import accounts_manager

# Load message texts
with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    accounts = accounts_manager.load_accounts()

    # Check if the user is already registered
    registered = any(account['telegram_id'] == str(chat_id) for account in accounts)

    if not registered:
        # Send registration prompt
        unregistered_names = accounts_manager.get_unregistered_names()
        buttons = [[InlineKeyboardButton(name, callback_data=f"register_{name}")] for name in unregistered_names]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(messages['start_registration'], reply_markup=reply_markup)
    else:
        await update.message.reply_text("You are already registered.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    name = query.data.split('_')[1]

    # Register the account
    if accounts_manager.register_account(name, str(chat_id)):
        await query.answer()
        await query.edit_message_text(text=messages['registration_success']['text'].replace("{name}", name))

        # Send success message with video
        await context.bot.send_message(chat_id=chat_id,
                                       text=messages['registration_success']['text'].replace("{name}", name))
        await context.bot.send_video(chat_id=chat_id, video=open(messages['registration_success']['video'], 'rb'))
    else:
        await query.answer("Registration failed. Please try again.")
