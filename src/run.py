import telebot
from libs.DB_binding import DB_binding
from libs.preprocessing import preprocessing
import re
from nltk import sent_tokenize
from Levenshtein import distance
import os
from dotenv import load_dotenv

load_dotenv('./.env')
token = os.environ.get('TOKEN')

a = DB_binding()
b = a.Sql("SELECT * FROM users;")

bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,f"Hello, World! :3 >{len(b)}<")

# askar's test some telebot functionality

@bot.message_handler(content_types=["text"])
def handle_text(message):
  bot.send_message(message.chat.id, preprocessing(message.text))

bot.infinity_polling()