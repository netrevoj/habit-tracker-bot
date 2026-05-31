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
            "У вас нет привычек для отображения статистики.",
            reply_markup=get_back_button()
        )
        await callback.answer()
        return

    text = "📊 <b>Ваша статистика:</b>\n\n"
    for habit in habits:
        stats = await db.get_habit_stats(habit['id'])
        text += (
            f"🔹 <b>{habit['name']}</b>\n"
            f"  • Текущая серия: {stats['current_streak']} дн.\n"
            f"  • Лучшая серия: {stats['best_streak']} дн.\n"
            f"  • Процент выполнения: {stats['completion_rate']}%\n"
            f"  • Всего выполнено: {stats['total_completions']}\n\n"
        )

    await callback.message.edit_text(text, reply_markup=get_back_button())
    await callback.answer()
