import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from tools import server, settings, database
from tools.settings import Configuration, StateMachine


logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(lambda message: message.text.lower().strip() not in ["нет", "да", 'готов'], state=StateMachine.first)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Неправильный ответ. Принимается только Да/Нет")

@dp.message_handler(lambda message: message.text.lower().strip() not in ["нет", "да"], state=StateMachine.second)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Неправильный ответ. Принимается только Да/Нет")


# Начало
@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    server_data = server.get_config_info()  # Нужен для отображения количества оставшихся вопросов
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Готов')
    await StateMachine.first.set()  # Показываем следующий вопрос
    await message.answer(f"Вопросов осталось: {server_data.count - server_data.current_index}")
    await message.answer('Для начала напишите мне - готов', reply_markup=markup)


@dp.message_handler(state=StateMachine.first)
async def get_question_1(message: types.Message, state: FSMContext):
    logging.info('STATE 1')
    server_data = server.get_config_info()
    try:
        if message.text.lower().strip() == 'нет':
            await StateMachine.rename.set()
            await message.answer('Напишите правильный вариант', reply_markup=types.ReplyKeyboardRemove())
            return
        elif message.text.lower().strip() == 'да':
            print('yo')
            if server_data.current_index == 0:
                server.update_skill(server_data.current_index)
            else:
                server.update_skill(server_data.current_index-1)
        server.update_config(Configuration(server_data.path, server_data.count, server_data.current_index+1, finished=False))
            
        question = server.get_skill(server_data.current_index)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('Нет', 'Да')
        await StateMachine.second.set()
        await message.answer(f"Правильно написано?\n-{question.name.capitalize()}\n"
                                f"Осталось: {server_data.count - server_data.current_index}",
                                reply_markup=markup)

    except IndexError:
        logging.error('INDEX ERROR')
        if not server_data.finished:
            await state.update_data(last_answer=message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('Завершить')
            await message.answer('❗Вопросы закончились!', reply_markup=markup)
            await StateMachine.last.set()


@dp.message_handler(state=StateMachine.second)
async def get_question_2(message: types.Message, state: FSMContext):
    logging.info('STATE 2')
    server_data = server.get_config_info()
    try:
        if message.text.lower().strip() == 'нет':
            await StateMachine.rename.set()
            await message.answer('Напишите правильный вариант', reply_markup=types.ReplyKeyboardRemove())
            return
        else:
            server.update_skill(server_data.current_index-1)

            server.update_config(Configuration(server_data.path, server_data.count, server_data.current_index + 1, finished=False))
            question = server.get_skill(server_data.current_index)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('Нет', 'Да')
            await StateMachine.first.set()
            await message.answer(f"Правильно написано?\n-{question.name.capitalize()}\n"
                                 f"Осталось: {server_data.count - server_data.current_index}",
                                 reply_markup=markup)

    except IndexError:
        logging.error('INDEX ERROR')
        if not server_data.finished:
            await state.update_data(last_answer=message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('Завершить')
            await message.answer('❗Вопросы закончились!', reply_markup=markup)
            await StateMachine.last.set()


@dp.message_handler(state=StateMachine.rename)
async def rename_func(message: types.Message, state:FSMContext):
    logging.info('RENAME STATE')
    try:
        server_data = server.get_config_info()
        server.update_skill(server_data.current_index - 1, new_value=message.text.capitalize())
        server.update_config(Configuration(server_data.path, server_data.count, server_data.current_index + 1, finished=False))

        question = server.get_skill(server_data.current_index)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('Нет', 'Да')
        await StateMachine.first.set()
        await message.answer(f"Правильно написано?\n-{question.name.capitalize()}\n"
                             f"Осталось: {server_data.count - server_data.current_index}",
                             reply_markup=markup)
    except IndexError:
        logging.error('INDEX ERROR')
        if not server_data.finished:
            await state.update_data(last_answer=message.text)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('Завершить')
            await message.answer('❗Вопросы закончились!', reply_markup=markup)
            await StateMachine.last.set()


# Завершение
@dp.message_handler(lambda message: message.text.lower().strip() in ["завершить"], state=StateMachine.last)
async def completion(message: types.Message, state: FSMContext):
    logging.info('LAST STATE')
    try:
        data = await state.get_data()  # Обрабатываем последний ответ
        if data['last_answer'].strip().lower() == 'нет':
            await StateMachine.rename.set()
            await message.answer('Напишите правильный вариант', reply_markup=types.ReplyKeyboardRemove())
    except BaseException as err:
        logging.error('Base ERROR')
        pass
    
    msg = await message.answer('⏱Отправляем результат...\n'
                               'Это может занять некоторое время',
                               reply_markup=types.ReplyKeyboardRemove())
    asyncio.create_task(delete_message(msg, 1))  # Удаляем вышеописанное сообщение через секунду
    result_path = server.show_results()

    if result_path:
        await message.answer('✅\tУспешно создали БД с отредактированными наименованиями\n')
        await bot.send_document(message.from_user.id, open(result_path,'rb'))
    else:
        await message.answer('😇БД уже отредактирована! ')


# Функция для удаления сообщений
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


if __name__ == "__main__":
    database.create_table(db_name=settings.SQL_NAME, table_name=settings.SQL_TABLE)
    executor.start_polling(dp, skip_updates=True)
