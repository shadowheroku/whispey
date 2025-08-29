import logging
import time
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler
from config import Config
from handlers.start import start
from handlers.inline import inline_query, handle_reveal_callback, handle_already_read_callback
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler
from handlers.start import start
from handlers.create import create_conversation
from handlers.list import list_whispers
from handlers.privacy import privacy, privacy_callback
from handlers.notifications import notifications, notifications_callback
from handlers.inline import inline_query, handle_reveal_callback
from handlers.reveal import reveal_handlers

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Create application
    application = Application.builder().token("8369183040:AAFWREA6Nhz9P6opj4d5zJiw2k5OnwWcfYk").build()

    # Add handlers
    application.add_handler(CommandHandler("start" , start))
    application.add_handler(CommandHandler("help" , start))
    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(CallbackQueryHandler(handle_reveal_callback, pattern="^reveal_"))
    application.add_handler(CallbackQueryHandler(handle_already_read_callback, pattern="^already_read"))
    application.add_handler(create_conversation)
    application.add_handler(CommandHandler("list", list_whispers))
    application.add_handler(CommandHandler("privacy", privacy))
    application.add_handler(CommandHandler("notifications", notifications))
    application.add_handler(CallbackQueryHandler(privacy_callback, pattern="^toggle_privacy$"))
    application.add_handler(CallbackQueryHandler(notifications_callback, pattern="^toggle_notifications$"))
    application.add_handler(CallbackQueryHandler(handle_reveal_callback, pattern="^reveal_"))

    application.add_handler(reveal_handlers)

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
