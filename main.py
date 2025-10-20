import os
import datetime
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command


load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

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

@dp.message(Command('time'))
async def time_command(message: Message):
    await message.answer(str(datetime.datetime.now()))

async def main():
    print("Bot starting...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())