from bot_logic import Bot_logic
from libs.DB_binding import DB_binding
from libs.message_handler import MessageHandler

import os, schedule, time, threading

import telebot
from telebot import types

from dotenv import load_dotenv
load_dotenv('./.env')
token = os.environ.get('TOKEN')
bot=telebot.TeleBot(token)

db = DB_binding()
handler = MessageHandler()
logic = Bot_logic()

logic.db = db
logic.modify_msg = handler
logic.send = bot.send_message

logic.init()

# handlers

@bot.message_handler(commands=['start'])
def start_message(message):
  logic.handler_commands('start', message.from_user.id)

@bot.message_handler(commands=['stop'])
def start_message(message):
  logic.handler_commands('stop', message.from_user.id)

@bot.message_handler(commands=['search'])
def start_message(message):
  logic.handler_commands('search', message.from_user.id)

@bot.message_handler(commands=['info'])
def start_message(message):
  logic.handler_commands('info', message.from_user.id)

@bot.message_handler(commands=['test'])
def start_message(message):
  logic.handler_commands('test', message.from_user.id)

# askar was here

@bot.message_handler(content_types=["text"])
def handle_text(message):
  logic.handler_message(message.from_user.id, message.text)

# callbacks

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  logic.handler_message(call.id, call.data, callback = True)


# utils

def create_buttons(arr: list):
  buttons = types.InlineKeyboardMarkup()
  for k, v in enumerate(arr):
    buttons.add( types.InlineKeyboardButton(v, callback_data=str(k)) )
  return buttons

logic.create_buttons = create_buttons

# run

#bot.infinity_polling()
if __name__ == '__main__':
  threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
  while True:
    schedule.run_pending()
    time.sleep(1)