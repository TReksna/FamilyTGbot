import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import registration
import finances
import photo_uploads

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

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
    application.add_handler(MessageHandler(filters.PHOTO, photo_uploads.handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, photo_uploads.handle_photo_name))

    # Start the bot
    application.run_polling()
