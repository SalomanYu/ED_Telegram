import openpyxl
import os
import json
from loguru import logger
from rich.progress import track
from professions_tools.preparation import Profession, IS_TECHNICAL_COLUMN, PROFESSION_COLUMN, PROFESSIONS_LIST_SHEET, JSON_PATH, PROFESSIONS_FOLDER


def update_all_files():
    print("Professions are over.")
    for file in track(range(len(os.listdir(PROFESSIONS_FOLDER))), description="[red]Update tables..."):
        xlsx_file = os.path.join(PROFESSIONS_FOLDER, os.listdir(PROFESSIONS_FOLDER)[file])
        if not xlsx_file.endswith(".xlsx"): continue
        professions = get_professions_by_path_XLSX_from_JSON(xlsx_file)
        if professions is None: continue
        update_XLSX(professions, xlsx_file)
    print("Program has done.")
    
def get_professions_by_path_XLSX_from_JSON(professionPath: str) -> list[Profession] | None:
    file = open(JSON_PATH, "r", encoding="utf-8")
    data = json.load(file)
    file.close()
    professions: list[Profession] = [Profession(*item.values()) for item in data if item['file'] == professionPath]
    if professions: return professions
    else: return None

def update_XLSX(professions: list[Profession], xlsx_file: str):
    try:
        book = openpyxl.load_workbook(xlsx_file)
    except KeyError: 
        logger.error(f"{xlsx_file} Поврежден и не может быть открыт!")
        return

    sheet = book[PROFESSIONS_LIST_SHEET]
    for profession in professions:set_profile_for_profession(sheet, profession)
    book.save(xlsx_file)

def set_profile_for_profession(sheet, profession: Profession):
    for i, row in enumerate(sheet.iter_rows()):
        row_values = list(row)
        if i == 0: row_values[IS_TECHNICAL_COLUMN].value = "Профиль"
        if profession.Title == row[PROFESSION_COLUMN].value:
            match profession.IsTechnical:
                case True: row_values[IS_TECHNICAL_COLUMN].value = "Технический"
                case False: row_values[IS_TECHNICAL_COLUMN].value = "Гуманитарный"
            logger.info(f"Записали профессию: {profession.Title}")
            break
