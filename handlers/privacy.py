from telegram import Update
from telegram.ext import ContextTypes
from storage import storage
from utils.keyboards import get_privacy_keyboard

async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show privacy settings"""
    user_id = update.effective_user.id
    user_data = storage.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("❌ Please start the bot first with /start")
        return
    
    privacy_enabled = user_data.get("privacy_mode", False)
    status = "enabled" if privacy_enabled else "disabled"
    
    explanation = """
🔒 Privacy Mode:
When enabled, your username won't be shown when you read whispers.
Instead, it will show "⏤͟͟͞𝗦ᴅᴡ ⌯ 𝐑ᴇᴅ 🍷 read the whisper".
"""
    
    await update.message.reply_text(
        f"{explanation}\nYour privacy mode is currently {status}.",
        reply_markup=get_privacy_keyboard(privacy_enabled)
    )

async def privacy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle privacy toggle callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = storage.get_user(user_id)
    
    if user_data:
        # Toggle privacy mode
        user_data["privacy_mode"] = not user_data.get("privacy_mode", False)
        storage.save_user(user_id, user_data)
        
        privacy_enabled = user_data["privacy_mode"]
        status = "enabled" if privacy_enabled else "disabled"
        
        await query.edit_message_text(
            f"✅ Privacy mode is now {status}.",
            reply_markup=get_privacy_keyboard(privacy_enabled)
        )
