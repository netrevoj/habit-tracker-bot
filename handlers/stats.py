from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from keyboards.inline import get_back_button

router = Router()

@router.callback_query(F.data == "view_stats")
async def view_stats(callback: CallbackQuery, db: Database):
    habits = await db.get_habits(callback.from_user.id)

    if not habits:
        await callback.message.edit_text(
            "You don't have any habits to show statistics for.",
            reply_markup=get_back_button()
        )
        await callback.answer()
        return

    text = "📊 <b>Your Statistics:</b>\n\n"
    for habit in habits:
        stats = await db.get_habit_stats(habit['id'])
        text += (
            f"🔹 <b>{habit['name']}</b>\n"
            f"  • Current Streak: {stats['current_streak']} days\n"
            f"  • Best Streak: {stats['best_streak']} days\n"
            f"  • Completion Rate: {stats['completion_rate']}%\n"
            f"  • Total Completions: {stats['total_completions']}\n\n"
        )

    await callback.message.edit_text(text, reply_markup=get_back_button())
    await callback.answer()
