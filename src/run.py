import telebot
from dotenv import load_dotenv
env = load_dotenv('.env')
token='5206536378:AAELOFjmqK_qPY7OGppdnEejFYEgbskNvvo'
bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,f"Hello, World >{env.TOKEN}< , >{env.TOKEN == token}<")
bot.infinity_polling()