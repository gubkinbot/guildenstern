import telebot
token='5206536378:AAELOFjmqK_qPY7OGppdnEejFYEgbskNvvo'
bot=telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,"Hello!")
bot.infinity_polling()