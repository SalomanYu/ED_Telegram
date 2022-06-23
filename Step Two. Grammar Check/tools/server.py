import json
import xlsxwriter

from . import settings
from .settings import Configuration, Skill

from . import database


def create_config_file(path: str) -> None:
    """Метод создает конфигурационный файл.
    Используется один раз, чтобы высчитать количество вопросов для нового файла с вопросами
    Принимает:
        path - путь до файла, в котором лежат уже обработанные вопросы"""
    data = json.load(open(path, 'r'))
    count = len(data)
    update_config(Configuration(path=path, count=count, current_index=0))


def get_config_info() -> Configuration:
    """Метод даёт актуальную информацию о конфигурационном файле
    Принимает:
        Configuration - именованный кортеж с общей информацией. Подробности в инициализации класса"""
    data = json.load(open('tools/config.json', 'r'))
    return Configuration(*tuple(data.values()))


def update_config(info: Configuration) -> None:
    print('Config changed!')
    """Метод позволяет обновлять конфигурационный файл.
    Обычно используется для того, чтобы обновить номер актуального вопроса
    Принимает:
        Configuration - именованный кортеж с общей информацией. Подробности в объявлении самого класса"""
    result = {
        'path': info.path,
        'count': info.count,
        'current_index': info.current_index,
        'finished': info.finished
    }
    with open('tools/config.json', 'w') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)


def get_skill(index) -> Skill:
    """Метод возвращает вопрос с номером, переданным в качестве аргумента
    Принимает:
        index - номер вопроса в списке файла с вопросами
    Возвращает:
        Question - именованный кортеж с общей информацией. Подробности в объявлении самого класса"""
    server_data = get_config_info()
    skills = json.load(open(server_data.path, 'r'))

    return Skill(*skills[index].values())


def update_skill(index: int, new_value: str=''):
    """Метод добавляет вопрос с номером, переданным в качестве аргумента
    Записывает в файл айди вопроса, который будет потом удален
    Принимает:
        index - номер вопроса в списке файла с вопросами"""
    data = json.load(open(settings.DATABASE_PATH,  'r'))
    question = data[index]
    question['new_name'] = new_value
    print(question['name'], '-----', question['new_name'])
    database.add(
        db_name=settings.SQL_NAME,
        table_name=settings.SQL_TABLE, 
        data=settings.RowData(old_name=question['name'],
                            new_name=question['new_name'],
                            id_num=question['id']))


    with open(settings.DATABASE_PATH, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def show_results() -> str:
    """Return path"""
    try:
        row = 0
        server_data = get_config_info()
        data = json.load(open(server_data.path, 'r'))
        # data = [{'1':'11', '2':'22'},{'3':'33', '4':'44'}]
        book = xlsxwriter.Workbook(settings.EXCEL_RESULT_FILENAME)
        sheet = book.add_worksheet()

        sheet.write(row, 0, 'id')
        sheet.write(row, 1, 'name')
        sheet.write(row, 2, 'edited_name')

        for item in data:
            row += 1
            sheet.write(row, 0, item['id'])
            sheet.write(row, 1, item['name'])
            sheet.write(row, 2, item['new_name'])
        book.close()

        update_config(Configuration(server_data.path, server_data.count, server_data.current_index, True))

        return settings.EXCEL_RESULT_FILENAME
    except BaseException as err:
        print('Произошла ошибка', err)

if __name__ == "__main__":
    # create_config_file(settings.DATABASE_PATH)
    show_results()