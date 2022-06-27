import sqlite3
from typing import NamedTuple
from aiogram.dispatcher.filters.state import State, StatesGroup


TOKEN = '5423038101:AAG-mktmRDpRE7GfuO1tk-ndA2GAh0g-cZY'
DATABASE_PATH = "../Data/mini_data_for_grammar_bot.json"
EXCEL_RESULT_FILENAME = "../Data/data_after_grammar_check.xlsx"

SQL_NAME = 'EditedSkills'
SQL_TABLE = 'Skills'


class Configuration(NamedTuple):
    """1.path - путь до конфиг-файла 2.count - количество вопросов 3.current_index - номер текущего вопроса 4.finished - состояние, указывающее на то, что бот закончил свою работу и обновил все наименования в файле"""
    path: str
    count: int
    current_index: int
    finished: bool


class Skill(NamedTuple):
    id: int
    name: str
    new_name: str


class StateMachine(StatesGroup):
    question = State()
    rename = State()
    last = State()


class Connection(NamedTuple):
    cursor: sqlite3.Connection
    db: sqlite3.Cursor


class RowData(NamedTuple):
    id_num: int
    old_name: str
    new_name: str