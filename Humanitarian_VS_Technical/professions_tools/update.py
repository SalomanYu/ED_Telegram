import openpyxl
import os
import json
from loguru import logger
from rich.progress import track
from professions_tools.preparation import Profession, IS_TECHNICAL_COLUMN, AREA_COLUMN, PROFESSION_COLUMN, PROFESSIONS_LIST_SHEET, JSON_PATH, PROFESSIONS_FOLDER


def update_all_files():
    print("Professions are over.")
    logger.warning("Заполняем excel-таблицы новыми значениями")
    professions = get_professions_from_json(JSON_PATH)
    for prof in track(range(len(professions)), description="[green]Update tables..."):
        find_and_update_profession_in_excelFile(professions[prof])
    print("Program has done.")
    

def get_professions_from_json(path: str) -> list[Profession]:
    file = open(path, "r", encoding="utf-8")
    data = json.load(file)
    file.close()
    return [Profession(*prof.values()) for prof in data]

def find_and_update_profession_in_excelFile(profession: Profession):
    for file in os.listdir(PROFESSIONS_FOLDER):
        if not file.endswith(".xlsx"): continue
        book = openpyxl.load_workbook(os.path.join(PROFESSIONS_FOLDER, file))
        sheet = book[PROFESSIONS_LIST_SHEET]
        for i, row in enumerate(sheet.iter_rows()):
            row_values = list(row)
            if i == 0: row_values[IS_TECHNICAL_COLUMN].value = "Профессия техническая?"
            if profession.Title == row_values[PROFESSION_COLUMN].value:
                match profession.IsTechnical:
                    case True: row_values[IS_TECHNICAL_COLUMN].value = 1
                    case False: row_values[IS_TECHNICAL_COLUMN].value = 0
                logger.info(f"Записали профессию: {profession.Title} в файл - {file}")
                book.save(os.path.join(PROFESSIONS_FOLDER, file))    
                return