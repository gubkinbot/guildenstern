import telebot
from libs.DB_binding import DB_binding
import re
from nltk import sent_tokenize
from Levenshtein import distance
import os
from dotenv import load_dotenv

nltk.download('punkt')

def preprocessing(question):
    question = re.sub(r'\s+', ' ', question) # удаление дублей в пробелах
    question = re.sub(r'(?<=[.,!?:;])(?=[^\s])', r' ', question) # вставка пробелов после знаков препинания
    question = re.sub('\s+(?=[,.!?])', '', question) # удаление пробелов перед знаками препинания
    primitive_phrases = [x.lower() for x in ['Как дела', 'Что делаешь', 'Чем занят', 'Как тебя звать', 'Как звать',
                                             'Как зовут', 'Что нового', 'Давай знакомиться']]
    array_sentences = sent_tokenize(question, language='russian')
    good = []
    bad = []
    for sentence in array_sentences:
        sentence = sentence[0].upper() + sentence[1:] # начинаем новое предложение с заглавной буквы
        if any(distance(sentence.lower(), x) < 4 for x in primitive_phrases): # пересечение со списком примитивных фраз
            bad.append(sentence)
        else:
            good.append(sentence)
    return 'good: ' + str(good) + 'bad:' + str(bad)


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