from aiogram.fsm.state import State, StatesGroup

class HabitStates(StatesGroup):
    waiting_for_habit_name = State()
