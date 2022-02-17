import os, dotenv
from aiogram import Bot, Dispatcher, executor, types
import logging


dotenv.load_dotenv('./.env')
token = os.environ.get('TOKEN')

bot = Bot(token)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)