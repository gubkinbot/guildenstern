import telebot
from libs.DB_binding import DB_binding
from libs.preprocessing import preprocessing
import os
from dotenv import load_dotenv

load_dotenv('./.env')
token = os.environ.get('TOKEN')

db = DB_binding()
users_counts = len(db.Sql("SELECT * FROM users;"))

bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):

  next_text = ""
  if not db.Get_id_from_tg_user_id(message.from_user.id):
    db.Add_user(message.from_user.id, 0)
    next_text = "\n\nYou added own database"

  bot.send_message(message.chat.id,f"Hello, World! :3 \n Users counts: {users_counts}\n Your telegram id: {message.from_user.id} {next_text}")
  

# askar's test some telebot functionality

@bot.message_handler(content_types=["text"])
def handle_text(message):
  bot.send_message(message.chat.id, preprocessing(message.text))

bot.infinity_polling()