import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, Application, JobQueue
import sheets_integration
import json
from datetime import datetime, time

# Load messages from JSON file
with open('messages.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)

QUESTION, RATING, FOLLOWUP = range(3)


async def start_checkin(update: Update, context: CallbackContext) -> int:
    keyboard = [[InlineKeyboardButton(messages['start_questions_button'], callback_data='start_checkin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(messages['checkin_prompt'], reply_markup=reply_markup)
    return QUESTION


async def start_questions(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat_id
    accounts = sheets_integration.load_accounts()
    user_name = accounts.get(str(user_id), 'Unknown')
    context.user_data['user_name'] = user_name

    questions = sheets_integration.get_checkin_questions()

    # Check if it's the first check-in by looking at the user's sheet
    user_responses = sheets_integration.get_recent_questions(user_name, days=0)  # Pass 0 days to get all responses
    if not user_responses:
        selected_questions = questions  # All 16 initial questions
    else:
        recent_questions = sheets_integration.get_recent_questions(user_name)
        questions_to_ask = [q for q in questions if q['Question'] not in recent_questions]
        random.shuffle(questions_to_ask)
        selected_questions = questions_to_ask[:4]

    context.user_data['questions'] = selected_questions
    context.user_data['current_question_index'] = 0

    return await ask_question(update, context)


async def ask_question(update: Update, context: CallbackContext) -> int:
    question_index = context.user_data['current_question_index']
    question = context.user_data['questions'][question_index]['Question']
    context.user_data['current_question'] = question

    keyboard = [
        [InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2')],
        [InlineKeyboardButton("3", callback_data='3')],
        [InlineKeyboardButton("4", callback_data='4'), InlineKeyboardButton("5", callback_data='5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if question_index > 0:
        question_text = f"{messages['next_question_prompt']} {messages['question_format'].format(number=question_index + 1, question=question)}"
    else:
        question_text = messages['question_format'].format(number=question_index + 1, question=question)

    if update.callback_query:
        await update.callback_query.edit_message_text(messages['rating_prompt'].format(question=question_text),
                                                      reply_markup=reply_markup)
    else:
        await update.message.reply_text(messages['rating_prompt'].format(question=question_text),
                                        reply_markup=reply_markup)

    return RATING


async def handle_rating(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    rating = int(query.data)
    context.user_data['rating'] = rating

    if rating in [1, 2, 4, 5]:
        return await ask_followup(update, context)
    else:
        await save_response(update, context, followup='')
        return await ask_question_or_finish(update, context)


async def ask_followup(update: Update, context: CallbackContext) -> int:
    question_index = context.user_data['current_question_index']
    question_data = context.user_data['questions'][question_index]
    rating = context.user_data['rating']

    followup_column = 'Positive' if rating in [4, 5] else 'Negative'
    followup_questions = [question_data[f'{followup_column}{i}'] for i in range(1, 4)]
    followup_question = random.choice([q for q in followup_questions if q])

    context.user_data['followup_question'] = followup_question

    if update.callback_query:
        await update.callback_query.edit_message_text(messages['followup_prompt'].format(question=followup_question))
    else:
        await update.message.reply_text(messages['followup_prompt'].format(question=followup_question))

    return FOLLOWUP


async def save_response(update: Update, context: CallbackContext, followup: str) -> None:
    user_name = context.user_data['user_name']
    question = context.user_data['current_question']
    rating = context.user_data['rating']
    date = datetime.now().strftime('%d.%m.%Y')

    sheets_integration.log_checkin_response(user_name, date, question, rating, followup)


async def ask_question_or_finish(update: Update, context: CallbackContext) -> int:
    question_index = context.user_data['current_question_index']
    if question_index < len(context.user_data['questions']) - 1:
        context.user_data['current_question_index'] += 1
        return await ask_question(update, context)
    else:
        if update.callback_query:
            await update.callback_query.message.reply_text(messages['thank_you_message'])
        else:
            await update.message.reply_text(messages['thank_you_message'])
        return ConversationHandler.END


async def handle_followup(update: Update, context: CallbackContext) -> int:
    followup = update.message.text
    await save_response(update, context, followup)
    return await ask_question_or_finish(update, context)


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(messages['cancel_message'])
    return ConversationHandler.END


def schedule_daily_checkin(job_queue: JobQueue):
    with open('tg_accounts.json', 'r', encoding='utf-8') as file:
        accounts = json.load(file)
    chat_ids = [account['telegram_id'] for account in accounts if account['telegram_id'] != 'Not Registered']
    for chat_id in chat_ids:
        job_queue.run_daily(checkin_job_callback, time=time(hour=16), days=(0, 1, 2, 3, 4, 5, 6),
                            data={'chat_id': chat_id})


def checkin_job_callback(context: CallbackContext):
    chat_id = context.job.data['chat_id']
    context.bot.send_message(chat_id=chat_id, text=messages['checkin_prompt'])
