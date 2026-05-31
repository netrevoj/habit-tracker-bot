from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    buttons = [
        [InlineKeyboardButton(text="➕ Add Habit", callback_data="add_habit")],
        [InlineKeyboardButton(text="📋 My Habits", callback_data="list_habits")],
        [InlineKeyboardButton(text="✅ Mark Completion", callback_data="track_habits")],
        [InlineKeyboardButton(text="📊 Statistics", callback_data="view_stats")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")]
    ])
