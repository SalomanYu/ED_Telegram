import sqlite3
from typing import NamedTuple
from aiogram.dispatcher.filters.state import State, StatesGroup


TOKEN = '5423038101:AAG-mktmRDpRE7GfuO1tk-ndA2GAh0g-cZY'
DATABASE_PATH = "/home/saloman/Documents/Edwica/Other/21.RepeatSkills/JSON/mini_data_for_grammar_bot.json"
EXCEL_RESULT_FILENAME = "/home/saloman/Documents/Edwica/Other/21.RepeatSkills/Result/data_after_grammar_check.xlsx"

SQL_NAME = 'EditedSkills'
SQL_TABLE = 'Skills'


class Configuration(NamedTuple):
    path: str
    count: int
    current_index: int
    finished: bool  # Флаг, чтобы понимать, что бот уже закончил работу и обновил все названия и файлы


class Skill(NamedTuple):
    id: int
    name: str
    new_name: str


class StateMachine(StatesGroup):
    first = State()
    second = State()
    rename = State()
    last = State()


class Connection(NamedTuple):
    cursor: sqlite3.Connection
    db: sqlite3.Cursor


class RowData(NamedTuple):
    id_num: int
    old_name: str
    new_name: str