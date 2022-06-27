"""Модуль, содержащий объявление основных объектов бота"""

from typing import NamedTuple
from aiogram.dispatcher.filters.state import State, StatesGroup

# Путь до excel-файла, в котором лежат исходные навыки, требующие очистки от дубликатов
DATABASE_PATH = '../../Data/course_skill.xlsx'
# Путь до тхт-файла, в который будут записываться айди навыков, которые следует удалить
DUPLICATES_FILE = '../../Data/duplicates.txt'
# Путь до json-файла, в котором будут лежать уже обработанные вопросы
LIST_FILTERED_QUESTIONS = '../../Data/mini_duplicate.json'
CONFIG_PATH = "tools/config.json"

TOKEN = "5512711126:AAF3S1c4-FdYUEB39GhjwAiQEQfpQ6x4R3U"


class Configuration(NamedTuple):
    path: str
    count: int
    current_index: int


class Question(NamedTuple):
    original: str
    duplicate: str
    percent: int
    id: int


class StateMachine(StatesGroup):
    question = State()
    last = State()
