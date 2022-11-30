import os
from loguru import logger

from aiogram import types, Bot, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio

from bot_config import StateMachine
from professions_tools import  db, update

TOKEN = os.getenv("HH_BOT")
bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logger.remove() # Запрещаем выводить сообщения в терминал
logger.add("Logging/bot.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", mode="w")
CURRENT_PROFESSION_ID = None


@dp.message_handler(commands="start")
async def run(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Готов")

    await StateMachine.start_question.set()
    await message.answer('Для начала напишите мне - готов', reply_markup=markup)
    logger.info(f"{message.from_user.username} Начал работу с ботом") 


@dp.message_handler(state=StateMachine.start_question)
async def start(message: types.Message, state: FSMContext):
    global CURRENT_PROFESSION_ID
    if message.text.lower() != "готов":
        asyncio.create_task(input_invalid(message))
        return
    profession = db.get_profession()
    if profession is None:
        logger.warning(f"{message.from_user.username}: Закончились вопросы!") 

        await message.answer("Все вопросы закончились! Спасибо", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        update.update_all_files()
        return
    CURRENT_PROFESSION_ID = profession.Id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Да')
    logger.info(f"{message.from_user.username}: {profession}") 

    await message.answer("\n".join((
        "Профессия техническая?",
        f"Профобласть: {profession.Area}",
        f"Название: {profession.Title}",
    )), reply_markup=markup)
    await StateMachine.question.set()

@dp.message_handler(state=StateMachine.question)
async def show_question(message: types.Message, state: FSMContext):
    global CURRENT_PROFESSION_ID
    if message.text.lower() not in {"да", "назад", "нет"}:
        asyncio.create_task(input_invalid(message))
        await state.finish()
        update.update_all_files()
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Назад', 'Да')

    if message.text.lower() == 'назад':
        previos_profession = db.get_last_edited_profession()
        if previos_profession:
            await StateMachine.question.set()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add('Нет', 'Назад', 'Да')
            logger.info(f"{message.from_user.username}: {previos_profession}") 
            await message.answer("\n".join((
                "Профессия техническая?",
                f"Профобласть: {previos_profession.Area}",
                f"Название: {previos_profession.Title}",
            )), reply_markup=markup)
            CURRENT_PROFESSION_ID = previos_profession.Id
        else:
            logger.warning(f"{message.from_user.username}: Попытка вернуться назад") 
            await message.answer("Ранее вы еще не отвечали на вопросы!")
    else:
        match message.text.lower():
            case "да": db.mark_profession_as_technical(CURRENT_PROFESSION_ID)
            case "нет": db.mark_profession_as_humanitarian(CURRENT_PROFESSION_ID)
        profession = db.get_profession()
        if profession is None:
            logger.warning(f"{message.from_user.username}: Закончились вопросы") 
            await message.answer("Все вопросы закончились! Спасибо", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            update.update_all_files()
            return
        CURRENT_PROFESSION_ID = profession.Id
        await message.answer("\n".join((
            "Профессия техническая?",
            f"Профобласть: {profession.Area}",
            f"Название: {profession.Title}",
        )), reply_markup=markup)
        await StateMachine.question.set()

# Обработка исключений
@dp.message_handler(state=StateMachine.question)
async def input_invalid(message: types.Message):
    await StateMachine.question.set()
    logger.warning(f"{message.from_user.username}: неправильный ответ") 
    return await message.reply("Неправильный ответ. Используйте клавиатуру или введите ответ самостоятельно")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
