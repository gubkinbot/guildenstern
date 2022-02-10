import telebot
from bot_logic import Bot_logic
from libs.DB_binding import DB_binding
from libs.message_handler import MessageHandler
from bot_logic import Bot_logic

import os
from dotenv import load_dotenv

load_dotenv('./.env')
token = os.environ.get('TOKEN')

db = DB_binding()
handler = MessageHandler()
logic = Bot_logic()

bot=telebot.TeleBot(token)

logic.db = db
logic.send = bot.send_message

@bot.message_handler(commands=['start'])
def start_message(message):
  logic.handler_start(message.from_user.id)

# askar's test some telebot functionality

@bot.message_handler(content_types=["text"])
def handle_text(message):
  bot.send_message(message.chat.id, handler.process(message.text))

bot.infinity_polling()