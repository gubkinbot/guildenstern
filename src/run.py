import telebot

import os
from dotenv import load_dotenv
load_dotenv('./.env')
token = os.environ.get('TOKEN')

bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,f"Hello, World! :3")
bot.infinity_polling()