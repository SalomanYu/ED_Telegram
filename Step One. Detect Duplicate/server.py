import json
import openpyxl

import settings
from settings import Configuration, Question


def create_config_file(path: str) -> None:
    """Метод создает конфигурационный файл.
    Используется один раз, чтобы высчитать количество вопросов для нового файла с вопросами
    Принимает:
        path - путь до файла, в котором лежат уже обработанные вопросы"""
    data = json.load(open(path, 'r'))
    count = len(data)
    post_config_info(Configuration(path=path, count=count, current_index=0))


def get_config_info() -> Configuration:
    """Метод даёт актуальную информацию о конфигурационном файле
    Принимает:
        Configuration - именованный кортеж с общей информацией. Подробности в инициализации класса"""
    data = json.load(open('config.json', 'r'))
    return Configuration(*tuple(data.values()))


def post_config_info(info: Configuration) -> None:
    """Метод позволяет обновлять конфигурационный файл.
    Обычно используется для того, чтобы обновить номер актуального вопроса
    Принимает:
        Configuration - именованный кортеж с общей информацией. Подробности в объявлении самого класса"""
    result = {
        'path': info.path,
        'count': info.count,
        'current_index': info.current_index
    }
    with open('config.json', 'w') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)


def get_question(index) -> Question:
    """Метод возвращает вопрос с номером, переданным в качестве аргумента
    Принимает:
        index - номер вопроса в списке файла с вопросами
    Возвращает:
        Question - именованный кортеж с общей информацией. Подробности в объявлении самого класса"""
    server_data = get_config_info()
    questions = json.load(open(server_data.path, 'r'))

    return Question(*questions[index].values())


def add_to_remove(index: int):
    """Метод добавляет вопрос с номером, переданным в качестве аргумента
    Записывает в файл айди вопроса, который будет потом удален
    Принимает:
        index - номер вопроса в списке файла с вопросами"""
    question = get_question(index)
    with open('/home/saloman/Documents/Edwica/Other/21.RepeatSkills/Result/duplicates.txt', 'a') as file:
        file.write(f"{question.id}\n")
    print(f'{[question.id]} Добавлен в список')


def clear_database() -> int:
    """Метод очищает БД(эксель-файл) от списка айди-вопросов из файла для удаления
    Возвращает:
        либо 0 - означающий, что нам нечего удалять
        либо количество навыков, которые мы удалили"""
    with open(settings.DUPLICATES_FILE, 'r') as file:
        items_for_remove = [int(i) for i in file.read().split('\n')[:-1]]  # -1 нужен чтобы не брать пустую строку

    if items_for_remove:  # Если есть что удалять
        book = openpyxl.load_workbook(settings.DATABASE_PATH)
        sheet = book.worksheets[0]
        for row in sheet.iter_rows():
            if row[0].value in items_for_remove:
                sheet.delete_rows(row[0].row)
                print(f'Deleted {row[0].value}')

        book.save(settings.DATABASE_PATH)
        print('Успешно сохранили файл')

        # Чистим файл с повторениями, потому что мы уже удалили все вопросы оттуда
        file = open(settings.DUPLICATES_FILE, 'w')
        file.close()
        return len(items_for_remove)
    else:
        return 0
        print('Nothing')


if __name__ == "__main__":
    create_config_file(settings.LIST_FILTERED_QUESTIONS)
