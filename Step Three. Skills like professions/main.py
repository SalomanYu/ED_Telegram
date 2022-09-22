from aiogram import Bot, executor, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from aiogram.dispatcher import FSMContext

import asyncio
from contextlib import suppress

import database
from config import StateMachine


bot = Bot(token="5630191911:AAHRae_J8oNLNLay6otNvbNcAd90yRwEz80")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

CURRENT_SKILL_ID = None

# Начало
@dp.message_handler(commands='start')
async def run_bot(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Готов')
    
    # Запускаем вспомогательный метод, с которого всё начнется 
    await StateMachine.start_question.set()  # Показываем следующий вопрос
    await message.answer('Для начала напишите мне - готов', reply_markup=markup)

@dp.message_handler(commands="professions")
async def show_professions(message: types.Message):
    professions = database.get_all_professions()
    if professions: 
        text = "\n".join([f"{index+1}. {value[0 ]}" for index, value in enumerate(professions)])
        await message.answer(f"Вот список профессий:\n {text}")
    else:
        await message.answer("Професси пока не были найдены")


@dp.message_handler( state=StateMachine.start_question)
async def start(message: types.Message):
    """Вспомогательный метод для запуска первого вопроса. Без этого метода, дублируются первые два вопросы и сбивается весь порядок ответов
    Поэтому был написан этот метод, как отправная точка и добавлена переменная CURRENT_QUESTION_ID"""

    global CURRENT_SKILL_ID
    if message.text.lower() != "готов":
        asyncio.create_task(input_invalid(message))
        return

    skill = database.get_not_viewed_skill()
    if not skill:
        await message.answer("Все вопросы закончились! Спасибо", reply_markup=types.ReplyKeyboardRemove())
        quit()
    # log.info("Couple: %s & %s", couple_skills.demand_name, couple_skills.dup_demand_name)
    CURRENT_SKILL_ID = skill.iD # Меняем значение нашей переменной, тем самым указывая корректный айди вопроса, который нужно обработать

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Да')
    await message.answer(f"Оставить навык?\n- {skill.title}", reply_markup=markup)
    await StateMachine.question.set()

# Переключение между вопросами 
@dp.message_handler(state=StateMachine.question)
async def show_question(message: types.Message, state: FSMContext):
    """
    Основной метод, который будет обрабатывать ответы пользователя и изменять значения в БД
    """
    global CURRENT_SKILL_ID
    if message.text.lower() not in {"да", "нет"}:
        asyncio.create_task(input_invalid(message))
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Да')

    # Меняем значения в БД
    if message.text.lower().strip() == 'да':
        database.set_confirm_skill(skill_id=CURRENT_SKILL_ID)
        # log.warning("Id: %d - Accept", CURRENT_QUESTION_ID)
    elif message.text.lower().strip() == 'нет':
        database.set_confirm_skill(skill_id=CURRENT_SKILL_ID, confirm=False)

        await StateMachine.profession_check.set() # Показываем следующий вопрос
        await message.answer(f"Этот навык похож на профессию?", reply_markup=markup)
        return

    # Получаем новый вопрос
    skill = database.get_not_viewed_skill()
    if not skill:
        await message.answer("Все вопросы закончились! Спасибо", reply_markup=types.ReplyKeyboardRemove())
        quit()
    CURRENT_SKILL_ID = skill.iD
    # log.info("Couple: %s & %s", couple_skills.demand_name, couple_skills.dup_demand_name)


    # Показываем вопрос пользователю
    await StateMachine.question.set() # Показываем следующий вопрос
    await message.answer(f"Оставить навык?\n- {skill.title}", reply_markup=markup)


@dp.message_handler(state=StateMachine.profession_check)
async def check_profession(message: types.Message, state: FSMContext):
    """Попадаем сюда, когда нам не подходит навык. Здесь будем уточнять является навык профессией или нет"""
    global CURRENT_SKILL_ID
    if message.text.lower() == "да":
        database.confirm_profession(skill_id=CURRENT_SKILL_ID)
    
    skill = database.get_not_viewed_skill()
    CURRENT_SKILL_ID = skill.iD
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Нет', 'Да')
    await StateMachine.question.set() # Показываем следующий вопрос
    await message.answer(f"Оставить навык?\n- {skill.title}", reply_markup=markup)


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



if __name__ == "__main__":
    dp.bot.set_my_commands([
        types.BotCommand(command="start", description='запустить бота'),
        types.BotCommand(command="professions", description='показать список профессий'),
        types.BotCommand(command="continue", description='продолжить работу с ботом'),
    ])
    executor.start_polling(dp, skip_updates=True)