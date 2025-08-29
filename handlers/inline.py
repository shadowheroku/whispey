import re
import time
import asyncio
from uuid import uuid4
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import ContextTypes
from config import Config
from storage import storage
from utils.keyboards import get_reveal_keyboard


# Max words allowed in popup (otherwise DM)
POPUP_WORD_LIMIT = 10


# ---------------------------
# Helpers
# ---------------------------
def parse_inline_query(query: str):
    """
    Parse inline query in the format:
    "whisper text here @username" or "whisper text here 123456789"
    Returns: (message, recipient, type) or (None, None, None)
    """
    query = query.strip()

    # Match @username
    username_match = re.search(r'@(\w+)$', query)
    if username_match:
        username = username_match.group(0)  # includes "@"
        message = query[:username_match.start()].strip()
        return message, username, "username"

    # Match user ID
    id_match = re.search(r'(\d+)$', query)
    if id_match:
        user_id = id_match.group(1)
        message = query[:id_match.start()].strip()
        return message, user_id, "id"

    return None, None, None


def count_words(text: str) -> int:
    """Count words in a text"""
    return len(text.split())


# ---------------------------
# Inline Query Handler
# ---------------------------
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return

    # Parse query
    message, recipient, recipient_type = parse_inline_query(query)

    if not message or not recipient:
        # Help message if wrong format
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="ℹ️ How to use this bot",
                input_message_content=InputTextMessageContent(
                    f"💬 To send a whisper, use this format:\n\n"
                    f"@{Config.BOT_USERNAME} your message @username\n\n"
                    f"or\n\n"
                    f"@{Config.BOT_USERNAME} your message 123456789"
                ),
                description="Type your secret message followed by @username or user ID",
                thumbnail_url="https://cdn-icons-png.flaticon.com/512/2955/2955806.png",
            )
        ]
        await update.inline_query.answer(results)
        return

    # Save whisper in storage
    whisper_id = storage.get_next_whisper_id()
    whisper_data = {
        "id": whisper_id,
        "sender_id": update.inline_query.from_user.id,
        "sender_name": update.inline_query.from_user.first_name,
        "recipient": recipient,
        "recipient_type": recipient_type,
        "message": message,
        "created_at": int(time.time()),
        "is_revealed": False,
        "revealed_by": None,
        "revealed_at": None,
        "word_count": count_words(message),
    }
    storage.save_whisper(whisper_id, whisper_data)

    # Display recipient
    display_recipient = recipient if recipient_type == "username" else f"user {recipient}"

    # Inline preview result
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"🔒 Whisper for {display_recipient}",
            input_message_content=InputTextMessageContent(
                f"🔒 A whisper for {display_recipient}\n\n"
                f"Only they can reveal this message."
            ),
            description=(message[:50] + "...") if len(message) > 50 else message,
            reply_markup=get_reveal_keyboard(whisper_id),
            thumbnail_url="https://cdn-icons-png.flaticon.com/512/2955/2955806.png",
        )
    ]

    await update.inline_query.answer(results, cache_time=0)  # no caching


# ---------------------------
# Reveal Whisper Callback
# ---------------------------
async def handle_reveal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not query.data.startswith("reveal_"):
        await query.answer()  # acknowledge invalid
        return

    whisper_id = int(query.data.split("_")[1])
    user_id = query.from_user.id
    username = query.from_user.username
    user_mention = f"@{username}" if username else query.from_user.first_name

    # Fetch whisper
    whisper = storage.get_whisper(whisper_id)
    if not whisper:
        await query.edit_message_text("❌ This whisper has expired or doesn’t exist.")
        return

    # Already revealed?
    if whisper.get("is_revealed", False):
        revealed_by = whisper.get("revealed_by", "someone")
        revealed_at = whisper.get("revealed_at", 0)
        time_ago = int(time.time()) - revealed_at

        if time_ago < 60:
            time_str = f"{time_ago} seconds ago"
        elif time_ago < 3600:
            time_str = f"{time_ago // 60} minutes ago"
        else:
            time_str = f"{time_ago // 3600} hours ago"

        await query.edit_message_text(
            f"👀 This whisper was already revealed by {revealed_by} ({time_str}).",
            reply_markup=None,
        )
        return

    # Check recipient
    recipient = whisper["recipient"]
    recipient_type = whisper["recipient_type"]

    is_recipient = False
    if recipient_type == "username":
        user_username = f"@{username}" if username else None
        is_recipient = user_username and (user_username.lower() == recipient.lower())
    else:  # by ID
        is_recipient = str(user_id) == recipient

    if not is_recipient:
        await query.answer("❌ This whisper is not for you!", show_alert=True)
        return

    # Deliver whisper
    message = whisper["message"]
    sender_name = whisper["sender_name"]
    word_count = whisper["word_count"]

    if word_count <= POPUP_WORD_LIMIT:
        # ✅ Show popup
        await query.answer(
            f"🔓 Whisper from {sender_name}:\n\n{message}",
            show_alert=True,
        )

        # Save as revealed
        whisper.update(
            {
                "is_revealed": True,
                "revealed_by": user_mention,
                "revealed_at": int(time.time()),
            }
        )
        storage.save_whisper(whisper_id, whisper)

        # ⏳ wait 3s before editing message
        await asyncio.sleep(1.5)

        await query.edit_message_text(
            f"👤 {user_mention} read the whisper.",
            reply_markup=None,
        )

    else:
        # Long whisper → DM
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🔓 Whisper from {sender_name}:\n\n{message}",
            )
            whisper.update(
                {
                    "is_revealed": True,
                    "revealed_by": user_mention,
                    "revealed_at": int(time.time()),
                }
            )
            storage.save_whisper(whisper_id, whisper)

            await asyncio.sleep(1.5)
            await query.edit_message_text(
                f"👤 {user_mention} read the whisper. (Sent to DM)",
                reply_markup=None,
            )
        except Exception:
            await query.answer(
                "❌ Could not deliver whisper. Please start a chat with me first!",
                show_alert=True,
            )


# ---------------------------
# Already Read Callback
# ---------------------------
async def handle_already_read_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ You’ve already read this message.", show_alert=True)
