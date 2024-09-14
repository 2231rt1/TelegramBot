from settings import TG_TOKEN
from telebot import *
bot = telebot.TeleBot(TG_TOKEN)
@bot.message_handler(commands = ['start'])
def main(message):
 bot.send_message(message.chat.id, '👋 Привет! Я твой помощник по маникюру! 💅\n С помощью меня ты можешь: \n\n * 💡 Посмотреть идеи для дизайна\n* 🗓 Записаться на процедуру к мастеру\n* 💅 Получить советы по уходу за ногтями \n\n Напиши мне "Помощь" или /help, чтобы узнать больше!') 


@bot.message_handler(commands = ['help'])
def main(message):
 bot.send_message(message.chat.id, 'Help information')


bot.polling(none_stop=True)




