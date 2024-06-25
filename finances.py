import json
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ContextTypes, ConversationHandler
import accounts_manager
import sheets_integration

# Expense logging states
NAME, AMOUNT, PURPOSE = range(3)

# Load message texts
with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)


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
