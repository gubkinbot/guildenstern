import telebot
import os
token='5206536378:AAELOFjmqK_qPY7OGppdnEejFYEgbskNvvo'
bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,f"Hello, World!!!! 5 >{os.environ.get('TOKEN')}< and >{os.getenv('TOKEN')}<")
bot.infinity_polling()