from aiogram.dispatcher.filters.state import State, StatesGroup

from typing import NamedTuple


class Skill(NamedTuple):
    iD: int
    title: str
    viewed: bool
    is_profession: bool


class StateMachine(StatesGroup):
    start_question = State()
    question = State()
    profession_check = State()
    last = State()