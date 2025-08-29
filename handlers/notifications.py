from telegram import Update
from telegram.ext import ContextTypes
from storage import storage
from utils.keyboards import get_notifications_keyboard

async def notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show notification settings"""
    user_id = update.effective_user.id
    user_data = storage.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("❌ Please start the bot first with /start")
        return
    
    notifications_enabled = user_data.get("notifications_enabled", True)
    status = "enabled" if notifications_enabled else "disabled"
    
    explanation = """
🔔 Notification Preferences:
When enabled, you'll receive notifications when someone sends you whispers
or when your whispers are read.
"""
    
    await update.message.reply_text(
        f"{explanation}\nYour notifications are currently {status}.",
        reply_markup=get_notifications_keyboard(notifications_enabled)
    )

async def notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle notifications toggle callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = storage.get_user(user_id)
    
    if user_data:
        # Toggle notifications
        user_data["notifications_enabled"] = not user_data.get("notifications_enabled", True)
        storage.save_user(user_id, user_data)
        
        notifications_enabled = user_data["notifications_enabled"]
        status = "enabled" if notifications_enabled else "disabled"
        
        await query.edit_message_text(
            f"✅ Notifications are now {status}.",
            reply_markup=get_notifications_keyboard(notifications_enabled)
        )
