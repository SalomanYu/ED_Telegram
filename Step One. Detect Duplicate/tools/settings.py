"""Модуль, содержащий объявление основных объектов бота"""
import os
import logging
from dataclasses import dataclass
from enum import Enum
from aiogram.dispatcher.filters.state import State, StatesGroup


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