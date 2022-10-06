from aiogram.dispatcher.filters.state import State, StatesGroup
import os
import logging

from typing import NamedTuple
from enum import Enum

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
    TABLE = "demand"

class Skill(NamedTuple):
    iD: int
    title: str
    is_dislayed: bool | None


class StateMachine(StatesGroup):
    start_question = State()
    question = State()
    # profession_check = State()
    last = State()

def start_logging(filename: str = "running_info.log") -> logging:
    # Перезаписываем файл
    log_file = open(filename, 'w') 
    log_file.close()
    
    logging.basicConfig(filename=filename, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    return logging