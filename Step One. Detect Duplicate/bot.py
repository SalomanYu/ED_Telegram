# coding=utf-8
import asyncio
from contextlib import suppress


from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext   
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from tools.settings import  StateMachine
from tools import settings
from tools import database
from loguru import logger


bot = Bot("5512711126:AAG71UBJSBDT_SFo29siLqo2kapcf-wSbcc")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Она появилась потому, что без этого бот будет считать предыдущее сообщение пользователя ответом на текущий вопрос (ответа на который ожидает бот)
# И когда пользователь введет да/нет, это автоматически запишется в ответ того вопроса, который должен появиться после этого ответа
# Эта переменная необходима для того, чтобы контролировать значения в состояниях ответов пользователя
CURRENT_QUESTION_ID = None 

logger.remove() # Запрещаем выводить сообщения в терминал
logger.add("LOGGING/bot.log", format="{time} {level} {message}", level="INFO", rotation="50 MB", compression="zip", mode="w")

# Начало
@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Готов')
    
    # Запускаем вспомогательный метод, с которого всё начнется 
    await StateMachine.start_question.set()  # Показываем следующий вопрос
    await message.answer(settings.WELCOME_TEXT)
    logger.info(f"[{message.from_user.username}] - Начал работу с ботом")
    await message.answer('Для начала напишите мне - готов', reply_markup=markup)


@dp.message_handler(state=StateMachine.start_question)
async def start(message: types.Message, state: FSMContext):
    """Вспомогательный метод для запуска первого вопроса. Без этого метода, дублируются первые два вопросы и сбивается весь порядок ответов
    Поэтому был написан этот метод, как отправная точка и добавлена переменная CURRENT_QUESTION_ID"""

    global CURRENT_QUESTION_ID
    if message.text.lower() != "готов":
        logger.info(f"[{message.from_user.username}] - Неправильный ответ")
        asyncio.create_task(input_invalid(message))
        return

    couple_skills = database.get_couple_skills_from_database()
    if not couple_skills:
        logger.warning(f"[{message.from_user.username}] - Вопросы закончились!")
        await message.answer("Все вопросы закончились! Спасибо", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    logger.info(f"[{message.from_user.username}] - Пара: {couple_skills.demand_name}&{couple_skills.dup_demand_name}")
    CURRENT_QUESTION_ID = couple_skills.id # Меняем значение нашей переменной, тем самым указывая корректный айди вопроса, который нужно обработать

    all_values, remains = database.get_how_much_is_left()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Да')
    await message.answer("\n".join((
                "Одинаковые навыки?",
                f"1️⃣ \t{couple_skills.demand_name.capitalize()}",
                f"1️⃣ \t{couple_skills.dup_demand_name.capitalize()}",
                f"🤔Совместимость: {couple_skills.similarity}%",
                f"Осталось:{remains}:{all_values}"
                )), reply_markup=markup)
    await StateMachine.question.set()


# Переключение между вопросами 
@dp.message_handler(state=StateMachine.question)
async def show_question(message: types.Message, state: FSMContext):
    """
    Основной метод, который будет обрабатывать ответы пользователя и изменять значения в БД
    """
    global CURRENT_QUESTION_ID
    if message.text.lower() not in {"да", "назад", "нет"}:
        asyncio.create_task(input_invalid(message))
        return

    # Меняем значения в БД
    if message.text.lower().strip() == "назад":
        logger.debug(f"[{message.from_user.username}] Back")
        previos_skill = database.get_last_viewed_skill()
        all_values, remains = database.get_how_much_is_left()
        if previos_skill:
            await StateMachine.question.set()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('Нет', 'Назад', 'Да')
            await message.answer("\n".join((
                "Одинаковые навыки?",
                f"1️⃣ \t{previos_skill.demand_name.capitalize()}",
                f"1️⃣ \t{previos_skill.dup_demand_name.capitalize()}",
                f"🤔Совместимость: {previos_skill.similarity}%",
                f"Осталось:{remains}:{all_values}"
                )), reply_markup=markup)
            logger.info(f"[{message.from_user.username}] - Пара: {previos_skill.demand_name}&{previos_skill.dup_demand_name}")
            CURRENT_QUESTION_ID = previos_skill.id
        else:
            await message.answer("Ранее вы еще не отвечали на вопросы. Ответьте на предыдущий вопрос")
        
        
    else:
        if message.text.lower().strip() == 'да':
            database.confirm_similarity(couple_id=CURRENT_QUESTION_ID)
            logger.warning(f"[{message.from_user.username}] - True: {CURRENT_QUESTION_ID}")

        elif message.text.lower().strip() == 'нет':
            logger.warning(f"[{message.from_user.username}] - False: {CURRENT_QUESTION_ID}")
            database.confirm_similarity(couple_id=CURRENT_QUESTION_ID, confirm=False)
        
        # Получаем новый вопрос
        couple_skills = database.get_couple_skills_from_database()
        if not couple_skills:     
            logger.warning(f"[{message.from_user.username}] - Вопросы закончились!")
            await message.answer("Все вопросы закончились! Спасибо", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
        logger.info(f"[{message.from_user.username}] - Пара: {couple_skills.demand_name}&{couple_skills.dup_demand_name}")
        CURRENT_QUESTION_ID = couple_skills.id
        
        # Показываем вопрос пользователю
        all_values, remains = database.get_how_much_is_left()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add('Нет', 'Назад', 'Да')
        await StateMachine.question.set() # Показываем следующий вопрос
        await message.answer("\n".join((
                "Одинаковые навыки?",
                f"1️⃣ \t{couple_skills.demand_name.capitalize()}",
                f"1️⃣ \t{couple_skills.dup_demand_name.capitalize()}",
                f"🤔Совместимость: {couple_skills.similarity}%",
                f"Осталось:{remains}:{all_values}"
                )), reply_markup=markup)


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
    executor.start_polling(dp, skip_updates=True)
