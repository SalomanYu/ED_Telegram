import xlrd
import os
import json
from typing import NamedTuple
from loguru import logger

class Profession(NamedTuple):
    Id          :int
    Title       :str
    Area        :str
    File        :str
    IsTechnical :bool | None

JSON_PATH = "Data/Json/prepared_data.json"
PROFESSIONS_FOLDER = "Data/Professions"
PROFESSIONS_LIST_SHEET = "Список профессий"
AREA_COLUMN = 2
PROFESSION_COLUMN = 5
IS_TECHNICAL_COLUMN = 6

def prepare_data() -> list[Profession]:
    data = []
    for file in os.listdir(PROFESSIONS_FOLDER):
        if not file.endswith(".xlsx"): continue
        professions = get_professions_from_file(os.path.join(PROFESSIONS_FOLDER, file))
        if professions is None: continue
        data += professions
        logger.info(f"Собрали все профессии из файла:{file} ")
    return data

def get_professions_from_file(FilePath: str) -> list[Profession]:
    professions: list[Profession] = []
    try:
        book = xlrd.open_workbook(FilePath)
    except xlrd.biffh.XLRDError:
        "Поврежденный xlsx-файл"
        logger.error(f"{FilePath} Поврежден и не может быть открыт!")
        return
    sheet = book.sheet_by_name(PROFESSIONS_LIST_SHEET)
    for row in range(1, sheet.nrows):
        row_values = sheet.row_values(row)
        is_technical = row_values[IS_TECHNICAL_COLUMN] if row_values[IS_TECHNICAL_COLUMN] != "" else None
        professions.append(Profession(
            Id=row,
            Title=row_values[PROFESSION_COLUMN],
            Area=row_values[AREA_COLUMN],
            File=FilePath,
            IsTechnical=is_technical
        ))
    return professions

def convert_data_to_json_format(data: list[Profession]) -> list[dict]:
    json_data = []
    for index, item in enumerate(data):
        match item.IsTechnical:
            case "Технический": is_techical = True
            case "Гуманитарный": is_techical = False
            case _: is_techical = None
        json_data.append({"id":index+1, "title":item.Title, "area":item.Area, "file":item.File, "is_technical":is_techical})
    return json_data


def save_to_json(data: list[dict]) -> None:
    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)