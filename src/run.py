import telebot
from libs.DB_binding import DB_binding
from libs.message_handler import MessageHandler
import os
from dotenv import load_dotenv

load_dotenv('./.env')
token = os.environ.get('TOKEN')

db = DB_binding()
handler = MessageHandler()

bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  users_counts = len(db.Sql("SELECT * FROM users;"))
  bot.send_message(message.chat.id,
  f'''
  Hello, World! :3
  Users counts: {users_counts}
  Your telegram id: {message.from_user.id}
  Your chad id: {message.chat.id}
  ''')
  
  if not db.Get_id_from_tg_user_id(message.from_user.id):
    db.Add_user(message.from_user.id, 0)
    bot.send_message(message.chat.id,f"You added own database")

# askar's test some telebot functionality

@bot.message_handler(content_types=["text"])
def handle_text(message):
  bot.send_message(message.chat.id, handler.process(message.text))

bot.infinity_polling()