import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from tools import settings, server
from tools.settings import Configuration, StateMachine

logging.basicConfig(level=logging.INFO)
bot = Bot(settings.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Начало
@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    server_data = server.get_config_info()  # Нужен для отображения количества оставшихся вопросов
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Готов')
    await StateMachine.question.set()  # Показываем следующий вопрос
    await message.answer(f"Вопросов осталось: {server_data.count - server_data.current_index}")
    await message.answer('Для начала напишите мне - готов', reply_markup=markup)


# Переключение между вопросами 
@dp.message_handler(lambda message: message.text.lower().strip() in ["да", "нет", 'готов'], state=StateMachine.question)
async def get_question_1(message: types.Message, state: FSMContext):
    server_data = server.get_config_info()
    try:
        if message.text.lower().strip() == 'да':
            # Если не отнимать единицу, то добавляется навык находящийся впереди нужного
            server.add_to_remove(server_data.current_index - 1)

        # Здесь мы получаем два навыка для сравнения, их инфу о совместимости и айди
        question = server.get_question(server_data.current_index)
        # Меняем номер актуального вопроса в конфиге
        server.post_config_info(Configuration(server_data.path, server_data.count, server_data.current_index + 1))

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('Нет', 'Да')
        await StateMachine.question.set() # Показываем следующий вопрос
        await message.answer(f"❔Это повторение?\n\n1️⃣ \t{question.original.capitalize()}\n"
                             f"2️⃣\t{question.duplicate.capitalize()}\n\n"
                             f"🤔Совместимость: {question.percent}%\n"
                             f"📶Осталось: {server_data.count - server_data.current_index}", reply_markup=markup)

    except IndexError:  # Если вопросы закончились
        # Запоминаем последний ответ, который нужно обрабатывать отдельно в последнем состоянии
        await state.update_data(last_answer=message.text)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('Завершить')
        await message.answer('❗Вопросы закончились!', reply_markup=markup)
        await StateMachine.last.set()  # Подключаем состояние завершения работы


# Завершение
@dp.message_handler(lambda message: message.text.lower().strip() in ["завершить"], state=StateMachine.last)
async def completion(message: types.Message, state: FSMContext):
    server_data = server.get_config_info()
    try:
        data = await state.get_data()  # Обрабатываем последний ответ
        if data['last_answer'].strip().lower() == 'да':
            server.add_to_remove(server_data.current_index - 1)
    except BaseException as err:
        pass

    msg = await message.answer('⏱Пробуем очистить БД от повторов...\n'
                               'Это может занять некоторое время',
                               reply_markup=types.ReplyKeyboardRemove())
    asyncio.create_task(delete_message(msg, 1))  # Удаляем вышеописанное сообщение через секунду

    duplicates_for_remove = server.clear_database()
    if duplicates_for_remove:
        await message.answer('✅\tУспешно очистили БД от повторов\n'
                             f'📉Удалили - {duplicates_for_remove} шт.')
        # await bot.send_document(message.from_user.id,
                                # open(settings.DATABASE_PATH,
                                    #  'rb'))
    else:
        await message.answer('😇БД уже очищена от повторов или список дубликатов пуст')


# Функция для удаления сообщений
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


# Обработка исключений
@dp.message_handler(lambda message: message.text.lower().strip() not in ["да", "нет", 'готов'],
                    state=StateMachine.question)
async def input_invalid(message: types.Message):
    return await message.reply("Неправильный ответ. Используйте клавиатуру или введите ответ самостоятельно")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
