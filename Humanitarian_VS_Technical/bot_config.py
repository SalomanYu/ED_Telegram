from aiogram.dispatcher.filters.state import State, StatesGroup

class StateMachine(StatesGroup):
    start_question = State()
    question = State()
    last = State()