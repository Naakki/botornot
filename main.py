import os
import datetime
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


load_dotenv()
storage = MemoryStorage()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(storage=storage)

class NewTaksStates(StatesGroup):
    task_title = State()

@dp.message(Command('start'))
async def start_command(message: Message):
    user_name = message.from_user.first_name
    await message.answer(f'Привет, {user_name}!\n \
                            Я еще учусь быть полезным. \
                            Если у тебя есть идеи, чем я моогу помочь, \
                            то обязательно сообщи об этом.\n\n\
                            /help - помощь\n\
                            /time - узнать время\n\
                            /say - обратная связь')
    
@dp.message(Command('help'))
async def help_command(message: Message):
    help_text = '''
        Доступные команды:

        /help - помощь
        /time - узнать время
        /say - обратная связь
                '''
    await message.answer(help_text)

@dp.message(Command('new_task'))
async def add_new_task(message: Message, state: FSMContext):
    await message.answer("✏️Введите задачу:")
    await state.set_state(NewTaksStates.task_title)

@dp.message(NewTaksStates.task_title, F.text)
async def set_task_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    user_data = await state.get_data()
    await message.answer(
        "📝Добавлена задача:\n\n"
        f" - {user_data['title']}",
        parse_mode="Markdown"
    )
    await state.clear()

@dp.message(Command('time'))
async def time_command(message: Message):
    await message.answer(str(datetime.datetime.now()))

async def main():
    print("Bot starting...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())