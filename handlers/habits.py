from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.db import Database
from utils.states import HabitStates
from keyboards.inline import get_main_menu, get_back_button

router = Router()

@router.callback_query(F.data == "add_habit")
async def start_add_habit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Please enter the name of your new habit:",
        reply_markup=get_back_button()
    )
    await state.set_state(HabitStates.waiting_for_habit_name)
    await callback.answer()

@router.message(HabitStates.waiting_for_habit_name)
async def process_habit_name(message: Message, state: FSMContext, db: Database):
    habit_name = message.text.strip()
    if not habit_name:
        await message.answer("Habit name cannot be empty. Please try again.")
        return

    await db.add_habit(message.from_user.id, habit_name)
    await state.clear()
    await message.answer(
        f"✅ Habit '{habit_name}' has been added!",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "list_habits")
async def list_habits(callback: CallbackQuery, db: Database):
    habits = await db.get_habits(callback.from_user.id)

    if not habits:
        await callback.message.edit_text(
            "You don't have any habits yet. Add one!",
            reply_markup=get_main_menu()
        )
        await callback.answer()
        return

    text = "📋 <b>Your Habits:</b>\n\n"
    buttons = []
    for habit in habits:
        text += f"• {habit['name']}\n"
        buttons.append([InlineKeyboardButton(text=f"❌ Delete {habit['name']}", callback_data=f"delete_{habit['id']}")])

    buttons.append([InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("delete_"))
async def delete_habit(callback: CallbackQuery, db: Database):
    habit_id = int(callback.data.split("_")[1])
    await db.delete_habit(habit_id)
    await callback.answer("Habit deleted!")
    await list_habits(callback, db)

@router.callback_query(F.data == "track_habits")
async def track_habits(callback: CallbackQuery, db: Database):
    from datetime import date
    today = date.today()
    habits = await db.get_habits(callback.from_user.id)

    if not habits:
        await callback.message.edit_text(
            "You don't have any habits to track. Add one!",
            reply_markup=get_main_menu()
        )
        await callback.answer()
        return

    text = f"✅ <b>Track Habits for {today.isoformat()}:</b>\n\n"
    buttons = []
    for habit in habits:
        is_done = await db.is_completed_today(habit['id'], today)
        status = "✅" if is_done else "⬜️"
        text += f"{status} {habit['name']}\n"

        if not is_done:
            buttons.append([InlineKeyboardButton(text=f"Mark {habit['name']} done", callback_data=f"complete_{habit['id']}")])

    buttons.append([InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("complete_"))
async def complete_habit(callback: CallbackQuery, db: Database):
    from datetime import date
    habit_id = int(callback.data.split("_")[1])
    success = await db.mark_completed(habit_id, date.today())
    if success:
        await callback.answer("Great job! Habit marked as completed.")
    else:
        await callback.answer("Already completed today!")
    await track_habits(callback, db)
