import os
import datetime
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from keyboard import get_main_keyboard, get_vote_keyboard, votes


load_dotenv()
storage = MemoryStorage()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(storage=storage)

class NewTaksStates(StatesGroup):
    task_title = State()

@dp.message(Command('start'))
async def start_command(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    await message.answer(f'''
Привет, {user_name} ({user_id})! Я еще учусь быть полезным. 
Если у тебя есть идеи, чем я моогу помочь, то 
обязательно сообщи об этом.

/help - помощь 
/time - узнать время 
/say - обратная связь
''',
reply_markup=get_main_keyboard())
    
@dp.message(F.text == "ℹ️Помощь")
async def help_message(message: Message):
    help_text = '''
Доступные команды:

/help - помощь
/time - узнать время
/say - обратная связь
                '''
    await message.answer(help_text)

@dp.message(F.text == "📝Добавить задачу")
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

@dp.message(F.text == "💭Обратная связь")
async def say_command(message: Message):
    await message.answer('Обратная связь:',
                         reply_markup=get_vote_keyboard())

@dp.message(F.photo)
async def photo_messages(message: Message):
    photo_id = message.photo[-1].file_id
    await message.answer("Принимаю только нудесы.")

@dp.message(F.document)
async def document_message(message: Message):
    doc_name = message.document.file_name
    doc_size = message.document.file_size
    await message.answer(
        f"Получен документ:\n\n"
        f"Название: {doc_name}\n"
        f"Размер: {doc_size/1000 } KB\n"
    )

@dp.callback_query(F.data.startswith("vote_"))
async def handle_vote(callback: CallbackQuery):
    vote_type = callback.data.split("_")[1] #like, dislike, love
    votes[vote_type] += 1

    await callback.message.edit_text(text="Обратная связь:",reply_markup=get_vote_keyboard())

@dp.message()
async def all_messages(message: Message):
    await message.delete()


# Главная функция (точка входа)
async def main():
    print("Bot starting...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop via creator...')