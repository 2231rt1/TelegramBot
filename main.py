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
            "Напиши мне /help, чтобы узнать больше!")

def format_help() -> str:
    """Format the help message."""
    return (
        "💅 Твой персональный эксперт по маникюру! ✨\n\n"
        "✨ <b>Хочешь идеальные ногти?</b> Я помогу! ✨\n\n"
        "Просто выбери нужный раздел в меню! 😉\n"
    )

def get_response(message_text: str) -> str:
    """Get the appropriate response based on user input."""
    responses = {
        "Хочу идеи для маникюра": "Here are some ideas for your manicure...",
        "Записаться на процедуру": "Let's schedule your appointment...",
        "Советы по уходу": "Here are some care tips for your nails...",
        "Фотогалерея": "Check out our photo gallery...",
        "Тест": "Doing test...",
        "Ногти и здоровье": "Learn how nail health affects your well-being...",
        "Модные тренды": "Discover the latest manicure trends...",
        "Цены и услуги": "Find out about our prices and services...",
    }
    return responses.get(message_text, "Прости, я не совсем тебя понимаю. Напиши /help.")

@bot.message_handler(commands=['start'])
def handle_start(message: types.Message):
    """Handle the start command and send a greeting with buttons."""
    greeting_text = format_greeting(message.from_user.first_name)
    markup = create_start_markup()
    send_message(message.chat.id, greeting_text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def handle_help(message: types.Message):
    """Handle the help command and send the help message."""
    help_text = format_help()
    markup = create_help_markup()
    send_message(message.chat.id, help_text, parse_mode='html', reply_markup=markup)

def create_start_markup() -> types.InlineKeyboardMarkup:
    """Create start menu markup with buttons."""
    buttons = [
        ("Хочу идеи для маникюра💅", 'Хочу идеи для маникюра'),
        ("Фотогалерея📸", 'Фотогалерея'),
        ("Тест💎", 'Тест'),
        ("Советы по уходу💖", 'Советы по уходу'),
        ("Ногти и здоровье🩺", 'Ногти и здоровье'),
        ("Модные тренды🔥", 'Модные тренды'),
        ("Записаться на процедуру🗓", 'Записаться на процедуру'),
        ("Цены и услуги💲", 'Цены и услуги'),
    ]

    markup = types.InlineKeyboardMarkup()
    for i in range(0, len(buttons), 2):
        row = buttons[i:i + 2]
        markup.add(*(types.InlineKeyboardButton(text, callback_data=callback) for text, callback in row))
        
    return markup

def create_help_markup() -> types.InlineKeyboardMarkup:
    """Create help menu markup."""
    return create_start_markup()  # Reuse the same buttons for help

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback: types.CallbackQuery):
    """Handle callback queries."""
    chat_id = callback.message.chat.id
    response = get_response(callback.data)
    send_message(chat_id, response)

@bot.message_handler(func=lambda message: True)  # Handle all other messages
def process_user_input(message: types.Message):
    """Process user input and handle queries."""
    response = get_response(message.text)
    send_message(message.chat.id, response)

# Start polling for new messages
if __name__ == "__main__":
    bot.polling(none_stop=True)
