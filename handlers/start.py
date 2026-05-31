from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Hi {message.from_user.full_name}! 👋\n"
        "Welcome to the Habit Tracker Bot. I can help you build good habits and track your progress.",
        reply_markup=get_main_menu()
    )

@router.callback_query(lambda c: c.data == "main_menu")
async def process_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Main Menu:",
        reply_markup=get_main_menu()
    )
    await callback.answer()
