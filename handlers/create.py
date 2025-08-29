from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from storage import storage
import time

# Conversation states
SELECT_RECIPIENT, SELECT_MEDIA = range(2)

# In-memory active whispers cache
ACTIVE_WHISPERS = {}


# Step 1: Start whisper creation
async def create_whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Let's create a whisper!\n\n"
        "Please enter the numeric ID of the recipient:"
    )
    return SELECT_RECIPIENT


# Step 2: Select recipient (numeric ID only)
async def select_recipient(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipient_input = update.message.text.strip()

    if not recipient_input.isdigit():
        await update.message.reply_text("❌ Invalid recipient. Please enter a numeric user ID only.")
        return SELECT_RECIPIENT

    recipient_id = int(recipient_input)

    # Save into conversation data
    context.user_data["recipient_id"] = str(recipient_id)
    context.user_data["recipient_display"] = recipient_id
    context.user_data["media_items"] = []

    await update.message.reply_text(
        f"✅ Recipient set: `{recipient_id}`\n\n"
        "Now send me the media/text for your whisper.\n"
        "➡️ Type /done when finished or /cancel to abort.",
        parse_mode="Markdown",
    )
    return SELECT_MEDIA


# Step 3: Collect media items
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    media_type, file_id, caption = None, None, update.message.caption

    if update.message.photo:
        media_type = "photo"
        file_id = update.message.photo[-1].file_id
    elif update.message.video:
        media_type = "video"
        file_id = update.message.video.file_id
    elif update.message.document:
        media_type = "document"
        file_id = update.message.document.file_id
    elif update.message.audio:
        media_type = "audio"
        file_id = update.message.audio.file_id
    elif update.message.voice:
        media_type = "voice"
        file_id = update.message.voice.file_id
    elif update.message.text:
        media_type = "text"

    if media_type:
        context.user_data["media_items"].append({
            "type": media_type,
            "file_id": file_id,
            "caption": caption,
            "text": update.message.text if media_type == "text" else None,
        })
        await update.message.reply_text(
            f"✅ {media_type.capitalize()} added!\n\n"
            "➡️ Send more or type /done to finish."
        )
    else:
        await update.message.reply_text("❌ Unsupported media type.")

    return SELECT_MEDIA


# Step 4: Finalize whisper
async def finish_whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("media_items"):
        await update.message.reply_text("❌ No media added. Whisper cancelled.")
        return ConversationHandler.END

    whisper_id = storage.get_next_whisper_id()
    whisper_data = {
        "id": whisper_id,
        "sender_id": update.effective_user.id,
        "recipient_id": context.user_data["recipient_id"],
        "recipient_display": context.user_data["recipient_display"],
        "media_items": context.user_data["media_items"],
        "created_at": int(time.time()),
        "is_revealed": False,
    }

    storage.save_whisper(whisper_id, whisper_data)
    ACTIVE_WHISPERS[str(whisper_id)] = whisper_data  # temporary cache

    # Inline button for reveal
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔒 Reveal Whisper", callback_data=f"reveal:{whisper_id}")]]
    )

    await update.message.reply_text(
        f"🤫 A whisper was created for {whisper_data['recipient_display']}\n\n"
        f"🆔 Whisper ID: `{whisper_id}`",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )

    context.user_data.clear()
    return ConversationHandler.END


# Cancel whisper creation
async def cancel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Whisper creation cancelled.")
    return ConversationHandler.END


# Step 5: Handle reveal


# Conversation handler
create_conversation = ConversationHandler(
    entry_points=[CommandHandler("create", create_whisper)],
    states={
        SELECT_RECIPIENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_recipient),
            CommandHandler("cancel", cancel_creation),
        ],
        SELECT_MEDIA: [
            MessageHandler(
                filters.PHOTO
                | filters.VIDEO
                | filters.Document.ALL
                | filters.AUDIO
                | filters.VOICE
                | (filters.TEXT & ~filters.COMMAND),
                handle_media,
            ),
            CommandHandler("done", finish_whisper),
            CommandHandler("cancel", cancel_creation),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_creation)],
)

# Reveal button handler

