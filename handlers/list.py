from telegram import Update
from telegram.ext import ContextTypes
from storage import storage
from utils.keyboards import get_whisper_action_keyboard

async def list_whispers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all whispers for the user"""
    user_id = update.effective_user.id
    whispers = storage.get_user_whispers(user_id, as_sender=True)
    
    if not whispers:
        await update.message.reply_text("📭 You don't have any pending whispers.")
        return
    
    message = "📋 Your pending whispers:\n\n"
    for whisper in whispers:
        status = "✅" if whisper.get("is_revealed") else "⏳"
        recipient = whisper.get("recipient", "Unknown")
        media_count = len(whisper.get("media_items", []))
        
        message += f"• ID: {whisper['id']} | To: {recipient} | Media: {media_count} | {status}\n"
    
    message += "\nUse /create to make more whispers!"
    await update.message.reply_text(message)
