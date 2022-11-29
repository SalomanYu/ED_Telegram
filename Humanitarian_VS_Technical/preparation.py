from professions_tools.preparation import prepare_data, save_to_json, convert_data_to_json_format, JSON_PATH
from loguru import logger 

logger.remove() # Запрещаем выводить сообщения в терминал
logger.add("Data/Logging/preparation.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", mode="w")

if __name__ == "__main__":
    data = prepare_data()
    logger.info("Собрали все профессии ")
    json_data = convert_data_to_json_format(data)
    logger.info("Переформатировали данные для записи в json")
    save_to_json(json_data)
    logger.info("Сохранили все профессии в один файл: ", JSON_PATH)
