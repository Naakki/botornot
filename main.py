import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from keyboard import get_main_keyboard, get_vote_keyboard, get_crud_task_key, votes
from service import NotesDatabase


load_dotenv()
notesdb = NotesDatabase()
storage = MemoryStorage()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(storage=storage)

class NewTaksStates(StatesGroup):
    task_title = State()
    task_comment = State()
    task_category = State()

class CRUDTaskStates(StatesGroup):
    operation = State()

def escape_markdown(text: str) -> str:
    """Экранирование специальных символов для MarkdownV2"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def format_quote(text: str) -> str:
    """Форматирует многострочный текст в цитату Markdown"""
    lines = text.split('\n')
    quoted_lines = [f"> {line}" for line in lines]
    return '\n'.join(quoted_lines)

@dp.message(Command('start'))
async def start_command(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    await notesdb.init_db()
    await message.answer(f'''
Привет, {user_name} ({user_id})! Я еще учусь быть полезным. 
Если у тебя есть идеи, чем я моогу помочь, то 
обязательно сообщи об этом.

/help - помощь 
/time - узнать время 
/say - обратная связь
''',
reply_markup=get_main_keyboard())
    
@dp.message(F.text == "🔧TODO list")
async def todolist(message: Message):
    todo_list = '''
1. Веб-сервис (веб-апп) для бота
2. Пагинация в списке задач
3. CRUD задач
4. Напоминалка
5. Настройки над задачами и уделомлениями
'''
    await message.answer(todo_list)
    
@dp.message(F.text == "ℹ️Помощь")
async def help_message(message: Message):
    help_text = '''
Доступные команды:

/help - помощь
/time - узнать время
/say - обратная связь
                '''
    await message.answer(help_text)

                                                        # Хендлеры для добавления задач Начало
@dp.message(F.text == "📝Добавить задачу")
async def add_new_task(message: Message, state: FSMContext):
    await message.answer("✏️Введите заголовок задачи:")
    await state.set_state(NewTaksStates.task_title)

@dp.message(NewTaksStates.task_title, F.text)
async def set_task_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await message.answer("✏️Введите комментарий:")
    await state.set_state(NewTaksStates.task_comment)

@dp.message(NewTaksStates.task_comment, F.text)
async def set_task_comment(message: Message, state: FSMContext):
    comment = message.text.strip()
    await state.update_data(comment=comment)
    await message.answer("✏️Введите категорию:")
    await state.set_state(NewTaksStates.task_category)

@dp.message(NewTaksStates.task_category, F.text)
async def set_task_comment(message: Message, state: FSMContext):
    category = message.text.strip()
    await state.update_data(category=category)
    user_data = await state.get_data()

    try:
        await notesdb.add_note(user_data)
        await message.answer(f"Добавлена новая задача: \n\n"
                             f"*{escape_markdown(user_data['title'])}*\n"
                             f"{format_quote(escape_markdown(user_data['comment']))}", 
                             parse_mode="MarkdownV2")
    except Exception as e:
        await message.answer(f"Что-то пошло не так: {e}")

    await state.clear()
                                                        # Хендлеры для добавления задач Конец

@dp.message(F.text == "📄Все задачи")
async def get_all_notes(message: Message):
    notes = await notesdb.get_all_notes()
    result = []

    if not notes:
        await message.answer("✅Все задачи выполнены!")
    else:
        for note in notes:
            safe_title = escape_markdown(note['title'])
            safe_comment = format_quote(escape_markdown(note['comment']))

            result.append(f"/task\\_{note['id']} *{safe_title}*\n"
                        f"{safe_comment}")
            
        await message.answer('\n\n'.join(result), parse_mode="MarkdownV2")

                                                        # Хендлеры для работы с задачами
@dp.message(F.text.startswith("/task_"))
async def get_task(message: Message, state: FSMContext):
    id = message.text.split('_')[1]

    if id.isdigit():
        task = await notesdb.get_note_by_id(id)

        if task:
            await state.update_data(id=id)
            await state.set_state(CRUDTaskStates.operation)
            await message.answer(f"/task\\_{task['id']} *{task['title']}*\n"
                                f"{format_quote(task['comment'])}",
                                parse_mode="MarkdownV2",
                                reply_markup=get_crud_task_key())
        else:
            await message.answer("❌Нет такой задачи")
    else:
        await message.delete()

@dp.callback_query(CRUDTaskStates.operation, F.data == "complete_task")
async def complete_task(callback: CallbackQuery, state: FSMContext):
    id = await state.get_data()
    await notesdb.delete_note(id['id'])

    notes = await notesdb.get_all_notes()
    result = []

    if not notes:
        await callback.message.edit_text("✅Все задачи выполнены!")
        await callback.answer()
    else:
        for note in notes:
            safe_title = escape_markdown(note['title'])
            safe_comment = format_quote(escape_markdown(note['comment']))

            result.append(f"/task\\_{note['id']} *{safe_title}*\n"
                        f"{safe_comment}")
        
        await callback.message.edit_text('\n\n'.join(result), parse_mode="MarkdownV2")
        await callback.answer("Задача выполнена ✅", show_alert=False)
    
    await state.clear()

@dp.callback_query(CRUDTaskStates.operation, F.data == "go_back_to_task_list")
async def go_back(callback: CallbackQuery, state: FSMContext):
    notes = await notesdb.get_all_notes()
    result = []

    if not notes:
        await callback.message.edit_text("✅Все задачи выполнены!")
    else:
        for note in notes:
            safe_title = escape_markdown(note['title'])
            safe_comment = format_quote(escape_markdown(note['comment']))

            result.append(f"/task\\_{note['id']} *{safe_title}*\n"
                          f"{safe_comment}")
        
        await callback.message.edit_text('\n\n'.join(result), parse_mode="MarkdownV2")
    await callback.answer()

                                                    # Хендлеры для работы с задачами Конец        

@dp.message(F.text == "💭Обратная связь")
async def say_command(message: Message):
    await message.answer('Обратная связь:', reply_markup=get_vote_keyboard())

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

    await callback.message.edit_text(text="Обратная связь:",
                                     reply_markup=get_vote_keyboard())

@dp.message()
async def all_messages(message: Message):
    await message.delete()


# Главная функция (точка входа)
async def main():
    print("Bot starting...")
    await notesdb.init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stop via creator...')