"""Модуль, содержащий объявление основных объектов бота"""
import os
import logging
from dataclasses import dataclass
from enum import Enum
from aiogram.dispatcher.filters.state import State, StatesGroup


WELCOME_TEXT = """Вам будет представлен список пар навыков, схожих по некоторому принципу. Вам нужно подвердить/опровергнуть сходство навыков.
        Какие навыки ЯВЛЯЮТСЯ дубликатами?
        1. Навык состоит из нескольких слов и отличается от другого навыка только порядком этих слов
        2. Навык похож по смыслу, но отличается по написанию
        Какие навыки НЕ ЯВЛЯЮТСЯ дубликатами?
        1. Если написание навыка индетично другому навыку, но у них отличается номер версии, то такие навыки НЕ ДУБЛИКАТЫ 
        Например: Python3 и Python2 - Два разных навыка
        Внимание: Python3.7 и Python3.10 - это уже одинаковые навыки, т.к первая целая часть версии, у них одинаковая
        """

TOKEN = os.getenv("DUPLICATE_REMOVER_TOKEN")
HOST = os.getenv("EDWICA_DB_HOST")
USER = os.getenv("EDWICA_DB_USER")
PASS = os.getenv("EDWICA_DB_PASS")

class MYSQL(Enum):
    HOST = HOST
    USER = USER
    PASSWORD = PASS
    PORT = 3306
    DB = "edwica_develop"
    TABLE = "demand_duplicate"

@dataclass
class SimilarCouple:
    id: int
    demand_id : int
    demand_name: str
    dup_demand_id: int
    dup_demand_name: str
    similarity: int
    is_duplicate: bool


class StateMachine(StatesGroup):
    start_question = State()
    question = State()
    last = State()


def start_logging(filename: str = "running_info.log"):
    # Перезаписываем файл
    log_file = open(filename, 'w') 
    log_file.close()
    
    logging.basicConfig(filename=filename, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    return logging