from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! 👋\n"
        "Добро пожаловать в бот для отслеживания привычек. Я помогу тебе сформировать полезные привычки и следить за прогрессом.",
        reply_markup=get_main_menu()
    )

@router.callback_query(lambda c: c.data == "main_menu")
async def process_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu()
    )
    await callback.answer()
