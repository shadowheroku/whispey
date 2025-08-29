from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_reveal_keyboard(whisper_id: int):
    """Create keyboard with reveal button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 Reveal Whisper", callback_data=f"reveal_{whisper_id}")]
    ])

def get_read_keyboard():
    """Create keyboard for read message"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Message Read", callback_data="already_read")]
    ])
from telegram import InlineKeyboardButton, InlineKeyboardMarkup



def get_privacy_keyboard(privacy_enabled: bool):
    """Create privacy settings keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"Privacy Mode: {'ON' if privacy_enabled else 'OFF'}",
                callback_data="toggle_privacy"
            )
        ]
    ])

def get_notifications_keyboard(notifications_enabled: bool):
    """Create notifications settings keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"Notifications: {'ON' if notifications_enabled else 'OFF'}",
                callback_data="toggle_notifications"
            )
        ]
    ])

def get_whisper_action_keyboard(whisper_id: int):
    """Create keyboard for whisper actions"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Edit", callback_data=f"edit_{whisper_id}"),
            InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{whisper_id}")
        ]
    ])
