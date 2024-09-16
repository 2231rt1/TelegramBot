import sqlite3
from telebot import TeleBot, types
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv('.env')
TG_TOKEN = os.getenv('TG_TOKEN')

bot = TeleBot(TG_TOKEN)

def create_appointments_table() -> None:
    """Create the appointments table if it doesn't exist."""
    conn = sqlite3.connect("appointments.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            chat_id INTEGER,
            appointment_date TEXT,
            appointment_time INTEGER
        )
    """)
    conn.commit()
    conn.close()

def send_message_with_markup(chat_id: int, text: str, markup: types.ReplyKeyboardMarkup) -> None:
    """Send a message to the user with a markup."""
    bot.send_message(chat_id, text, parse_mode='html', reply_markup=markup)

def format_greeting_message(first_name: str) -> str:
    """Format the greeting message."""
    return (
        f"Привет, {first_name}! Я твой помощник по маникюру! 💅\n"
        "С помощью меня ты можешь:\n\n"
        "* Посмотреть идеи для дизайна\n"
        "* Записаться на процедуру к мастеру\n"
        "* Получить советы по уходу за ногтями\n\n"
        "Напиши мне /help, чтобы узнать больше!"
    )

def format_help_message() -> str:
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

def handle_appointment_message(message: types.Message) -> None:
    """Handle appointment message."""
    today = datetime.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    dates = [today, tomorrow]
    
    # Connect to the database
    conn = sqlite3.connect("appointments.db")
    c = conn.cursor()
    
    # Get existing appointments for the next two days
    c.execute("SELECT appointment_date, appointment_time FROM appointments WHERE appointment_date IN (?, ?)", (today, tomorrow))
    existing_appointments = c.fetchall()
    
    # Create a set to store unavailable time slots
    unavailable_time_slots = set()
    
    # Iterate over existing appointments and add time slots to the set
    for appointment in existing_appointments:
        date = appointment[0]
        time = appointment[1]
        unavailable_time_slots.add((date, time))
    
    # Create the appointment markup
    markup = create_appointment_markup(dates, unavailable_time_slots)
    
    # Send the message with the markup
    send_message_with_markup(message.chat.id, "Выберите время для записи на процедуру:", markup)
    
    # Close the database connection
    conn.close()

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

def create_appointment_markup(dates, unavailable_time_slots):
    """Create appointment markup."""
    markup = types.InlineKeyboardMarkup()
    buttons = []
    
    # Iterate over dates and time slots
    for date in dates:
        for time in range(16, 23, 2):  # 16:00 to 22:00 with 2-hour intervals
            # Check if the time slot is available
            if (date, time) not in unavailable_time_slots:
                button_text = f"{time}:00"
                callback_data = f"appointment_{date}_{time}"
                buttons.append(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    
    # Add the buttons to the markup
    markup.add(*buttons)
    
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
        "записаться на процедуру": handle_appointment_message,
        "цены и услуги": "Find out about our prices and services... 💲",
    }
    # Convert input to lowercase for case-insensitive matching
    message_text = message_text.lower()
    # Remove the sticker (emoji) from the button text
    message_text = message_text.rstrip("💅📸💎💖🩺🔥🗓💲")
    return responses.get(message_text, "Sorry, I don't understand that. Please try again.")

@bot.message_handler(commands=['start'])
def handle_start(message: types.Message) -> None:
    """Handle the start command and send the greeting message."""
    first_name = message.from_user.first_name
    greeting_text = format_greeting_message(first_name)
    markup = create_help_markup()
    send_message_with_markup(message.chat.id, greeting_text, markup)

@bot.message_handler(commands=['help'])
def handle_help(message: types.Message) -> None:
    """Handle the help command and send the help message."""
    help_text = format_help_message()
    markup = create_help_markup()
    send_message_with_markup(message.chat.id, help_text, markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("appointment_"))
def handle_appointment_callback(callback: types.CallbackQuery) -> None:
    """Handle appointment callback queries."""
    chat_id = callback.message.chat.id
    appointment_data = callback.data.split("_")
    date = appointment_data[1]
    appointment_time = int(appointment_data[2])
    response = f"Вы выбрали {appointment_time}:00 для записи на процедуру в {date}."
    bot.send_message(chat_id, response)

@bot.message_handler(content_types=['text'])
def handle_text_message(message: types.Message) -> None:
    """Handle text messages and respond accordingly."""
    response = get_response(message.text)
    if callable(response):
        response(message)
    else:
        bot.send_message(message.chat.id, response)

if __name__ == "__main__":
    create_appointments_table()
    bot.polling()