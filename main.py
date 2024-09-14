from settings import TG_TOKEN
from telebot import TeleBot, types

# Initialize the bot with the provided token
bot = TeleBot(TG_TOKEN)

def send_message(chat_id: int, text: str, parse_mode: str = None, reply_markup: types.InlineKeyboardMarkup = None):
    """Helper function to send a message."""
    bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)

def format_greeting(first_name: str) -> str:
    """Format the greeting message."""
    return (f"👋 Привет, {first_name}! Я твой помощник по маникюру! 💅\n"
            "С помощью меня ты можешь:\n\n"
            "* 💡 Посмотреть идеи для дизайна\n"
            "* 🗓 Записаться на процедуру к мастеру\n"
            "* 💅 Получить советы по уходу за ногтями\n\n"
            "Напиши мне /help, чтобы узнать больше!")

def format_help() -> str:
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

def handle_user_query(message_text: str, chat_id: int, first_name: str):
    """Handle specific user queries."""
    responses = {
        "Хочу идеи для маникюра": "Here are some ideas for your manicure...",
        "Записаться на процедуру": "Let's schedule your appointment...",
        "Советы по уходу": "Here are some care tips for your nails...",
        "Фотогалерея": "Check out our photo gallery...",
        "Ногти и здоровье": "Learn how nail health affects your well-being...",
        "Модные тренды": "Discover the latest manicure trends...",
        "Цены и услуги": "Find out about our prices and services...",
    }

    response = responses.get(message_text, 
                              f"Прости, {first_name}, я не совсем тебя понимаю. Напиши /help.")
    send_message(chat_id, response)

@bot.message_handler(commands=['start'])
def handle_start(message: types.Message):
    """Handle the start command and send a greeting."""
    greeting_text = format_greeting(message.from_user.first_name)
    send_message(message.chat.id, greeting_text)

@bot.message_handler(commands=['help'])
def handle_help(message: types.Message):
    """Handle the help command and send the help message."""
    help_text = format_help()
    markup = create_help_markup()
    send_message(message.chat.id, help_text, parse_mode='html', reply_markup=markup)

def create_help_markup() -> types.InlineKeyboardMarkup:
    """Create help menu markup."""
    buttons = [
        ("Записаться на процедуру🗓", 'send'),
        ("Хочу идеи для маникюра💅", 'send'),
        ("Фотогалерея📸", 'send'),
        ("Советы по уходу💖", 'send'),
        ("Ногти и здоровье🩺", 'send'),
        ("Модные тренды🔥", 'send'),
        ("Цены и услуги💲", 'send'),
    ]

    markup = types.InlineKeyboardMarkup()
    for i in range(0, len(buttons), 2):
        row = buttons[i:i + 2]
        markup.add(*(types.InlineKeyboardButton(text, callback_data=callback) for text, callback in row))
        
    return markup

@bot.message_handler(func=lambda message: True)  # Handle all other messages
def process_user_input(message: types.Message):
    """Process user input and handle queries."""
    handle_user_query(message.text, message.chat.id, message.from_user.first_name)

# Start polling for new messages
if __name__ == "__main__":
    bot.polling(none_stop=True)
