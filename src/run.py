import telebot
import os
token=os.environ.get('TOKEN')
bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,"Hello, World!")
bot.infinity_polling()