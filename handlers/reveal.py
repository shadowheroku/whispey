import asyncio
from telegram import (
    Update,
    InputMediaPhoto,
    InputMediaVideo,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CommandHandler, ContextTypes
from storage import storage


async def auto_delete(sent_messages, confirm_msg, delay: int = 30):
    """Background task to auto-delete messages after delay."""
    await asyncio.sleep(delay)
    try:
        for msg in sent_messages:
            await msg.delete()
        await confirm_msg.delete()
    except Exception:
        pass  # ignore if already deleted


async def reveal_whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reveal a whisper by ID (only allowed for the recipient, auto-deleted after reveal)."""
    if update.effective_chat.type != "private":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔓 Reveal in DM", url=f"https://t.me/{context.bot.username}?start=reveal")]]
        )
        await update.message.reply_text(
            "⚠️ For privacy, whispers can only be revealed in DM.\n\n"
            "Click below to continue:",
            reply_markup=keyboard,
        )
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a whisper ID. Example:\n`/reveal ABCDE`",
            parse_mode="Markdown",
        )
        return

    whisper_id = context.args[0].strip()
    whisper = storage.get_whisper(whisper_id)

    if not whisper:
        await update.message.reply_text("❌ Whisper not found.")
        return

    if whisper.get("is_revealed"):
        await update.message.reply_text("⚠️ This whisper has already been revealed.")
        return

    recipient_id = str(whisper.get("recipient_id"))
    if recipient_id != str(update.effective_user.id):
        await update.message.reply_text("🚫 You are not the recipient of this whisper.")
        return

    media_items = whisper.get("media_items", [])
    sent_messages = []

    if len(media_items) == 1:
        item = media_items[0]
        if item["type"] == "photo":
            msg = await update.message.reply_photo(item["file_id"], caption=item.get("caption"))
        elif item["type"] == "video":
            msg = await update.message.reply_video(item["file_id"], caption=item.get("caption"))
        elif item["type"] == "document":
            msg = await update.message.reply_document(item["file_id"], caption=item.get("caption"))
        elif item["type"] == "audio":
            msg = await update.message.reply_audio(item["file_id"], caption=item.get("caption"))
        elif item["type"] == "voice":
            msg = await update.message.reply_voice(item["file_id"], caption=item.get("caption"))
        elif item["type"] == "text":
            msg = await update.message.reply_text(item["text"])
        sent_messages.append(msg)

    else:
        album = []
        standalone_items = []

        for i, item in enumerate(media_items):
            caption = item.get("caption") if i == 0 else None
            if item["type"] == "photo":
                album.append(InputMediaPhoto(item["file_id"], caption=caption))
            elif item["type"] == "video":
                album.append(InputMediaVideo(item["file_id"], caption=caption))
            else:
                standalone_items.append((item, caption))

        if album:
            msgs = await update.message.reply_media_group(album)
            sent_messages.extend(msgs)

        for item, caption in standalone_items:
            if item["type"] == "document":
                msg = await update.message.reply_document(item["file_id"], caption=caption)
            elif item["type"] == "audio":
                msg = await update.message.reply_audio(item["file_id"], caption=caption)
            elif item["type"] == "voice":
                msg = await update.message.reply_voice(item["file_id"], caption=caption)
            elif item["type"] == "text":
                msg = await update.message.reply_text(item["text"])
            sent_messages.append(msg)

    whisper["is_revealed"] = True
    storage.save_whisper(whisper_id, whisper)

    confirm_msg = await update.message.reply_text(
        "🎉 Whisper revealed successfully!\n\n⚠️ This content will be auto-deleted in 30 seconds."
    )

    # 🚀 Run auto-delete as background task (non-blocking)
    asyncio.create_task(auto_delete(sent_messages, confirm_msg, delay=30))


# Add handler
reveal_handlers = CommandHandler("reveal", reveal_whisper)
