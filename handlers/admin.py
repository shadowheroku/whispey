from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from config import Config
from storage import storage
from utils.keyboards import get_admin_keyboard

# States for broadcast conversation
BROADCAST_MESSAGE = range(1)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != Config.OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    await update.message.reply_text(
        "Admin panel:",
        reply_markup=get_admin_keyboard()
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id != Config.OWNER_ID:
        await query.edit_message_text("You are not authorized to use this command.")
        return
    
    action = query.data
    
    if action == "admin_stats":
        stats = storage.get_stats()
        message = f"""
📊 Bot Statistics:
• Total Users: {stats['users']}
• Total Whispers: {stats['total']}
• Read Whispers: {stats['read']}
• Unread Whispers: {stats['unread']}
        """
        await query.edit_message_text(message, reply_markup=get_admin_keyboard())
    
    elif action == "admin_list_users":
        users = storage.get_all_users()
        message = "👥 Users:\n\n"
        for user_id, user in list(users.items())[:10]:  # Show first 10 users
            message += f"• {user.get('first_name', 'Unknown')} (@{user.get('username', 'N/A')}) - ID: {user_id}\n"
        
        if len(users) > 10:
            message += f"\n... and {len(users) - 10} more users."
        
        await query.edit_message_text(message, reply_markup=get_admin_keyboard())
    
    elif action == "admin_list_whispers":
        whispers = storage.get_all_whispers()
        message = "📨 Whispers:\n\n"
        for whisper_id, whisper in list(whispers.items())[:10]:  # Show first 10 whispers
            status = "✓" if whisper.get("is_read", False) else "✗"
            message += f"• #{whisper_id}: From {whisper.get('sender_id')} to {whisper.get('recipient')} {status}\n"
        
        if len(whispers) > 10:
            message += f"\n... and {len(whispers) - 10} more whispers."
        
        await query.edit_message_text(message, reply_markup=get_admin_keyboard())
    
    elif action == "admin_broadcast":
        await query.edit_message_text(
            "Please enter the broadcast message:",
            reply_markup=None
        )
        return BROADCAST_MESSAGE

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != Config.OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return ConversationHandler.END
    
    message = update.message.text
    users = storage.get_all_users()
    
    # Store message in context for confirmation
    context.user_data['broadcast_message'] = message
    context.user_data['broadcast_users'] = list(users.keys())
    
    await update.message.reply_text(
        f"Are you sure you want to broadcast this message to {len(users)} users?\n\n"
        f"Message: {message}\n\n"
        "Type /confirm to proceed or /cancel to abort."
    )
    
    return BROADCAST_MESSAGE

async def confirm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != Config.OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return ConversationHandler.END
    
    message = context.user_data.get('broadcast_message')
    users = context.user_data.get('broadcast_users', [])
    
    if not message or not users:
        await update.message.reply_text("Broadcast data missing. Please start over.")
        return ConversationHandler.END
    
    # Send broadcast to all users
    success = 0
    failures = 0
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 Broadcast from admin:\n\n{message}")
            success += 1
        except Exception as e:
            failures += 1
    
    await update.message.reply_text(
        f"Broadcast completed!\n"
        f"✅ Success: {success}\n"
        f"❌ Failures: {failures}"
    )
    
    return ConversationHandler.END

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Broadcast cancelled.")
    return ConversationHandler.END

# Create conversation handler for broadcast
broadcast_conversation = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r'^/admin_broadcast$'), admin)],
    states={
        BROADCAST_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message),
            MessageHandler(filters.Regex(r'^/confirm$'), confirm_broadcast),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex(r'^/cancel$'), cancel_broadcast)]
)
