from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Banner image (you can replace this with your own)
    banner_url = "https://files.catbox.moe/0k53oj.jpg"

    welcome_text = f"""
<b>✨ Welcome, {update.effective_user.first_name}! 👋</b>

🤫 I’m <b>{context.bot.username}</b> — your personal <i>Whisper Bot</i>.  
I let you send <b>secret one-time whispers</b> inside groups or private chats.

🔐 <u>How to use me</u>:  
Type → <code>@{context.bot.username} your secret text @username</code>  
Only the chosen user can unlock it once!

📌 <u>Available Commands</u>  
<b>/create</b> – Create an advanced whisper (supports all media & albums)  
<b>/list</b> – View your current pending whispers  
<b>/privacy</b> – Toggle privacy mode (hide read receipts)  
<b>/notifications</b> – Manage whisper notifications via a settings panel  

✨ Keep your chats private, mysterious, and fun!
    """

    # Inline buttons
    buttons = [
        [
            InlineKeyboardButton("📢 Support Channel", url="https://t.me/shadowbotshq"),
            InlineKeyboardButton("💬 Support Group", url="https://t.me/shadowchathq"),
        ],
        [
            InlineKeyboardButton("👑 Owner", url="https://t.me/hey_redd")
        ]
    ]

    await update.message.reply_photo(
        photo=banner_url,
        caption=welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )
