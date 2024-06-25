import os
import json
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ContextTypes, ConversationHandler
from dotenv import load_dotenv
import accounts_manager
import sheets_integration

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

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


# Expense logging states
NAME, AMOUNT, PURPOSE = range(3)


async def izmaksas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    registered_names = accounts_manager.get_registered_names()
    buttons = [[InlineKeyboardButton(name, callback_data=f"expense_{name}")] for name in registered_names]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(messages['log_expense_start'], reply_markup=reply_markup)
    return NAME


async def expense_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data['name'] = query.data.split('_')[1]
    await query.answer()
    await query.edit_message_text(
        text=messages['log_expense_amount_prompt'].replace("{name}", context.user_data['name']))
    return AMOUNT


async def expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = update.message.text
    name = context.user_data['name']
    await update.message.reply_text(
        messages['log_expense_purpose_prompt'].replace("{name}", name).replace("{amount}", update.message.text))
    return PURPOSE


async def expense_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['purpose'] = update.message.text
    name = context.user_data['name']
    amount = context.user_data['amount']
    purpose = update.message.text
    date_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    telegram_id = update.message.chat_id

    # Log the expense
    sheets_integration.log_expense(telegram_id, name, amount, purpose, date_time)

    success_message = messages['log_expense_success'].replace("{name}", name).replace("{amount}", amount).replace(
        "{purpose}", purpose)
    await update.message.reply_text(success_message, parse_mode='Markdown')
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('izmaksas', izmaksas)],
        states={
            NAME: [CallbackQueryHandler(expense_name, pattern='^expense_')],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, expense_amount)],
            PURPOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, expense_purpose)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern='^register_'))
    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()
