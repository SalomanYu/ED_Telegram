import json
from professions_tools.preparation import Profession, save_to_json

JSONPATH = "Data/Json/prepared_data.json"


def get_profession() -> Profession | None:
    data = json.load(open(JSONPATH, "r", encoding="utf-8"))
    try:
        item = next((prof for prof in data if prof["is_technical"] is None))
        return Profession(*item.values())
    except StopIteration:
        return None

def get_last_edited_profession() -> Profession | None:
    data = json.load(open(JSONPATH, "r", encoding="utf-8"))
    try:
        item = next((data[i-1] for i in range(len(data), 0, -1) if data[i-1]["is_technical"]  is not None))
        unmark_profession(item["id"])
        return Profession(*item.values())
    except StopIteration:
        return None

def mark_profession_as_technical(prof_id: int) -> None:
    data = json.load(open(JSONPATH, "r", encoding="utf-8"))
    for item in data:
        if item["id"] == prof_id:
            item["is_technical"] = True
            break
    save_to_json(data)

def mark_profession_as_humanitarian(prof_id: int) -> None:
    data = json.load(open(JSONPATH, "r", encoding="utf-8"))
    for item in data:
        if item["id"] == prof_id:
            item["is_technical"] = False
            break
    save_to_json(data)

def unmark_profession(prof_id: int) -> None: # Опровергнуть сходство
    data = json.load(open(JSONPATH, "r", encoding="utf-8"))
    for item in data:
        if item["id"] == prof_id:
            item["is_technical"] = None
            break
    save_to_json(data)


    