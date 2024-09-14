from settings import TG_TOKEN
from telebot import TeleBot

# Initialize the bot with the provided token
bot = TeleBot(TG_TOKEN)

def send_message(chat_id, text, parse_mode=None):
    """Helper function to send a message."""
    bot.send_message(chat_id, text, parse_mode=parse_mode)

def format_greeting(first_name):
    """Format the greeting message."""
    return (
        f"👋 Привет, {first_name}! Я твой помощник по маникюру! 💅\n"
        "С помощью меня ты можешь:\n\n"
        "* 💡 Посмотреть идеи для дизайна\n"
        "* 🗓 Записаться на процедуру к мастеру\n"
        "* 💅 Получить советы по уходу за ногтями\n\n"
        "Напиши мне 'Помощь' или /help, чтобы узнать больше!"
    )

def format_help():
    """Format the help message."""
    return (
        "💅 Твой персональный эксперт по маникюру! ✨\n\n"
        "✨ <b>Хочешь идеальные ногти?</b> Я помогу! ✨\n\n"
        "Просто напиши мне:\n\n"
        "* <b>Хочу идеи для маникюра</b>: 💅 Я покажу тебе самые модные дизайны...\n"
        "* <b>Записаться на процедуру</b>: 🗓 Я помогу найти мастера...\n"
        "* <b>Советы по уходу</b>: 💖 Я поделюсь секретами ухода за ногтями...\n"
        "* <b>Фотогалерея</b>: 📸 Хочешь вдохновиться? Посмотри фото...\n"
        "* <b>Ногти и здоровье</b>: 🩺 Узнай о здоровье ногтей...\n"
        "* <b>Модные тренды</b>: 🔥 Я расскажу о самых модных тенденциях...\n"
        "* <b>Цены и услуги</b>: 💲 Узнай больше о стоимости услуг...\n\n"
        "Или выбери нужный <b><u>раздел</u></b> в меню бота! 😉\n"
        "Начни прямо сейчас! ✨"
    )

def handle_user_query(message_text, chat_id, first_name):
    """Handle specific user queries."""
    responses = {
        "Хочу идеи для маникюра": "Here are some ideas for your manicure...",
        "Записаться на процедуру": "Let's schedule your appointment...",
        "Советы по уходу": "Here are some care tips for your nails...",
        "Фотогалерея": "Check out our photo gallery...",
        "Ногти и здоровье": "Learn how nail health affects your well-being...",
        "Модные тренды": "Discover the latest manicure trends...",
        "Цены и услуги": "Find out about our prices and services..."
    }
    
    response = responses.get(message_text, f"Прости, {first_name}, я не совсем тебя понимаю. Напиши 'Помощь' или /help.")
    send_message(chat_id, response)

@bot.message_handler(commands=['start'])
def handle_start(message):
    greeting_text = format_greeting(message.from_user.first_name)
    send_message(message.chat.id, greeting_text)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = format_help()
    send_message(message.chat.id, help_text, parse_mode='html')

@bot.message_handler(func=lambda message: True)  # Handle all other messages
def info(message):
    handle_user_query(message.text, message.chat.id, message.from_user.first_name)

# Start polling for new messages
bot.polling(none_stop=True)
