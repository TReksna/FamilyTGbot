import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ConversationHandler
import registration
import finances
import photo_uploads
import checkin

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Initialize JobQueue
    job_queue = application.job_queue

    # Registration Handlers
    application.add_handler(CommandHandler("start", registration.start))
    application.add_handler(CallbackQueryHandler(registration.button, pattern='^register_'))

    # Finances Handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('izmaksas', finances.izmaksas)],
        states={
            finances.NAME: [CallbackQueryHandler(finances.expense_name, pattern='^expense_')],
            finances.AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, finances.expense_amount)],
            finances.PURPOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, finances.expense_purpose)],
        },
        fallbacks=[CommandHandler('cancel', finances.cancel)],
    )
    application.add_handler(conv_handler)

    # Photo Upload Handlers
    photo_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, photo_uploads.handle_photo)],
        states={
            photo_uploads.PHOTO_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, photo_uploads.handle_photo_name)],
        },
        fallbacks=[CommandHandler('cancel', photo_uploads.cancel)],
    )
    application.add_handler(photo_conv_handler)

    # Check-in Handlers
    checkin_handler = ConversationHandler(
        entry_points=[CommandHandler('checkin', checkin.start_checkin)],
        states={
            checkin.QUESTION: [CallbackQueryHandler(checkin.start_questions, pattern='^start_checkin$')],
            checkin.RATING: [CallbackQueryHandler(checkin.handle_rating, pattern='^[1-5]$')],
            checkin.FOLLOWUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkin.handle_followup)],
        },
        fallbacks=[CommandHandler('cancel', checkin.cancel)],
    )
    application.add_handler(checkin_handler)

    # Schedule daily check-in message
    checkin.schedule_daily_checkin(job_queue)

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
