from settings import TG_TOKEN
from telebot import TeleBot, types

bot = TeleBot(TG_TOKEN)

def send_message(chat_id: int, text: str, parse_mode: str = None, reply_markup: types.InlineKeyboardMarkup = None) -> None:
    """Send a message to the user."""
    bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)

def format_greeting(first_name: str) -> str:
    """Format the greeting message."""
    return (
        f"Привет, {first_name}! Я твой помощник по маникюру! 💅\n"
        "С помощью меня ты можешь:\n\n"
        "* Посмотреть идеи для дизайна\n"
        "* Записаться на процедуру к мастеру\n"
        "* Получить советы по уходу за ногтями\n\n"
        "Напиши мне /help, чтобы узнать больше!"
    )

def format_help() -> str:
    """Format the help message."""
    return (
        "Твой персональный эксперт по маникюру! ✨\n\n"
        "Хочешь идеальные ногти? Я помогу! ✨\n\n"
        "Просто напиши мне:\n\n"
        "* Хочу идеи для маникюра💅: Я покажу тебе самые модные дизайны...\n"
        "* Фотогалерея📸: Хочешь вдохновиться? Посмотри фото...\n"
        "* Тест💎: Какой стиль маникюра тебе подходит?\n"
        "* Советы по уходу💖: Я поделюсь секретами ухода за ногтями...\n"
        "* Ногти и здоровье🩺: Узнай о здоровье ногтей...\n"
        "* Модные тренды🔥: Я расскажу о самых модных тенденциях...\n"
        "* Цены и услуги💲: Узнай больше о стоимости услуг...\n\n"
        "Или выбери нужный раздел в меню бота! 😉\n"
        "Начни прямо сейчас! ✨"
    )

def create_help_markup() -> types.ReplyKeyboardMarkup:
    """Create help menu markup."""
    buttons = [
        [
            types.KeyboardButton("Хочу идеи для маникюра💅"),
            types.KeyboardButton("Фотогалерея📸"),
        ],
        [
            types.KeyboardButton("Тест💎"),
            types.KeyboardButton("Советы по уходу💖"),
        ],
        [
            types.KeyboardButton("Ногти и здоровье🩺"),
            types.KeyboardButton("Модные тренды🔥"),
        ],
        [
            types.KeyboardButton("Записаться на процедуру🗓"),
            types.KeyboardButton("Цены и услуги💲"),
        ],
    ]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in buttons:
        markup.add(*row)

    return markup

def get_response(message_text: str) -> str:
    """Get the appropriate response based on user input."""
    responses = {
        "хочу идеи для маникюра": "Here are some ideas for your manicure... 💅",
        "фотогалерея": "Check out our photo gallery... 📸",
        "тест": "Doing test... 💎",
        "советы по уходу": "Here are some care tips for your nails... 💖",
        "ногти и здоровье": "Learn how nail health affects your well-being... 🩺",
        "модные тренды": "Discover the latest manicure trends... 🔥",
        "записаться на процедуру": "Let's schedule your appointment... 🗓",
        "цены и услуги": "Find out about our prices and services... 💲",
    }
    # Convert input to lowercase for case-insensitive matching
    message_text = message_text.lower()
    # Remove the sticker (emoji) from the button text
    message_text = message_text.rstrip("💅📸💎💖🩺🔥🗓💲")
    return responses.get(message_text, "Sorry, I don't understand that. Please try again.")

@bot.message_handler(commands=['start'])
def handle_start(message: types.Message) -> None:
    """Handle the start command and send a greeting."""
    greeting_text = format_greeting(message.from_user.first_name)
    send_message(message.chat.id, greeting_text)

@bot.message_handler(commands=['help'])
def handle_help(message: types.Message) -> None:
    """Handle the help command and send the help message."""
    help_text = format_help()
    markup = create_help_markup()
    send_message(message.chat.id, help_text, parse_mode='html', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback: types.CallbackQuery) -> None:
    """Handle callback queries."""
    chat_id = callback.message.chat.id
    response = get_response(callback.data)
    send_message(chat_id, response)

@bot.message_handler(func=lambda message: True)  # Handle all other messages
def process_user_input(message: types.Message) -> None:
    """Process user input and handle queries."""
    response = get_response(message.text)
    send_message(message.chat.id, response)

if __name__ == "__main__":
    bot.polling(none_stop=True)