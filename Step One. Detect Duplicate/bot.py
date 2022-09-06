import asyncio
import logging
from contextlib import suppress
import os


from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from tools.settings import  StateMachine
from tools import settings
from tools import database


bot = Bot(settings.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Она появилась потому, что без этого бот будет считать предыдущее сообщение пользователя ответом на текущий вопрос (ответа на который ожидает бот)
# И когда пользователь введет да/нет, это автоматически запишется в ответ того вопроса, который должен появиться после этого ответа
# Эта переменная необходима для того, чтобы контролировать значения в состояниях ответов пользователя
CURRENT_QUESTION_ID = None 


# Начало
@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Готов')
    
    # Запускаем вспомогательный метод, с которого всё начнется 
    await StateMachine.start_question.set()  # Показываем следующий вопрос
    await message.answer('Для начала напишите мне - готов', reply_markup=markup)


@dp.message_handler(state=StateMachine.start_question)
async def start(message: types.Message):
    """Вспомогательный метод для запуска первого вопроса. Без этого метода, дублируются первые два вопросы и сбивается весь порядок ответов
    Поэтому был написан этот метод, как отправная точка и добавлена переменная CURRENT_QUESTION_ID"""

    global CURRENT_QUESTION_ID
    if message.text.lower() != "готов":
        asyncio.create_task(input_invalid(message))
        return

    couple_skills = database.get_couple_skills_from_database()
    log.info("Couple: %s & %s", couple_skills.demand_name, couple_skills.dup_demand_name)
    CURRENT_QUESTION_ID = couple_skills.id # Меняем значение нашей переменной, тем самым указывая корректный айди вопроса, который нужно обработать

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Да')
    await message.answer(f"❔Одинаковые навыки?\n\n"
                        f"1️⃣ \t{couple_skills.demand_name.capitalize()}\n"
                        f"2️⃣\t{couple_skills.dup_demand_name.capitalize()}\n\n"
                        f"🤔Совместимость: {couple_skills.similarity}%\n", reply_markup=markup)
    await StateMachine.question.set()


# Переключение между вопросами 
@dp.message_handler(state=StateMachine.question)
async def show_question(message: types.Message, state: FSMContext):
    """
    Основной метод, который будет обрабатывать ответы пользователя и изменять значения в БД
    """
    global CURRENT_QUESTION_ID
    if message.text.lower() not in {"да", "нет"}:
        asyncio.create_task(input_invalid(message))
        return

    # Меняем значения в БД
    if message.text.lower().strip() == 'да':
        database.confirm_similarity(couple_id=CURRENT_QUESTION_ID)
        log.warning("Id: %d - Accept", CURRENT_QUESTION_ID)
    elif message.text.lower().strip() == 'нет':
        log.info("Id: %d - Failed", CURRENT_QUESTION_ID)
        database.confirm_similarity(couple_id=CURRENT_QUESTION_ID, confirm=False)

    # Получаем новый вопрос
    couple_skills = database.get_couple_skills_from_database()
    CURRENT_QUESTION_ID = couple_skills.id
    log.info("Couple: %s & %s", couple_skills.demand_name, couple_skills.dup_demand_name)


    # Показываем вопрос пользователю
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Да')
    await StateMachine.question.set() # Показываем следующий вопрос
    await message.answer(f"❔Одинаковые навыки?\n\n"
                            f"1️⃣ \t{couple_skills.demand_name.capitalize()}\n"
                            f"2️⃣\t{couple_skills.dup_demand_name.capitalize()}\n\n"
                            f"🤔Совместимость: {couple_skills.similarity}%\n", reply_markup=markup)


# Функция для удаления сообщений
async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


# Обработка исключений
@dp.message_handler(state=StateMachine.question)
async def input_invalid(message: types.Message):
    await StateMachine.question.set()
    return await message.reply("Неправильный ответ. Используйте клавиатуру или введите ответ самостоятельно")


if __name__ == '__main__':
    log = settings.start_logging()
    executor.start_polling(dp, skip_updates=True)
