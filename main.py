import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command
from aiogram import Router
from dotenv import load_dotenv
import os

# Загрузка токена из .env файла
load_dotenv('.env')
TG_TOKEN = os.getenv('TG_TOKEN')

# Инициализация бота
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
router = Router()

# Создание таблицы записей
def create_appointments_table() -> None:
    """Создание таблицы для записей, если её нет."""
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

# Асинхронная функция для отправки сообщения с разметкой
async def send_message_with_markup(chat_id: int, text: str, markup: ReplyKeyboardMarkup) -> None:
    """Отправка сообщения пользователю с клавиатурой."""
    await bot.send_message(chat_id, text, parse_mode='html', reply_markup=markup)

# Форматирование приветственного сообщения
def format_greeting_message(first_name: str) -> str:
    """Форматирование приветственного сообщения."""
    return (
        f"Привет, {first_name}! Я твой помощник по маникюру! 💅\n"
        "С помощью меня ты можешь:\n\n"
        "* Посмотреть идеи для дизайна\n"
        "* Записаться на процедуру к мастеру\n"
        "* Получить советы по уходу за ногтями\n\n"
        "Напиши мне /help, чтобы узнать больше!"
    )

# Форматирование сообщения помощи
def format_help_message() -> str:
    """Форматирование сообщения помощи."""
    return (
        "Твой персональный эксперт по маникюру! ✨\n\n"
        "Просто напиши мне:\n\n"
        "* Хочу идеи для маникюра💅: Я покажу тебе самые модные дизайны...\n"
        "* Фотогалерея📸: Хочешь вдохновиться? Посмотри фото...\n"
        "* Тест💎: Какой стиль маникюра тебе подходит?\n"
        "* Советы по уходу💖: Я поделюсь секретами ухода за ногтями...\n"
        "* Ногти и здоровье🩺: Узнай о здоровье ногтей...\n"
        "* Модные тренды🔥: Я расскажу о самых модных тенденциях...\n"
        "* Цены и услуги💲: Узнай больше о стоимости услуг...\n"
    )

# Создание разметки для раздела помощи
def create_help_markup() -> ReplyKeyboardMarkup:
    """Создание клавиатуры для меню помощи."""
    buttons = [
        [
            types.KeyboardButton(text="Хочу идеи для маникюра💅"),
            types.KeyboardButton(text="Фотогалерея📸"),
        ],
        [
            types.KeyboardButton(text="Тест💎"),
            types.KeyboardButton(text="Советы по уходу💖"),
        ],
        [
            types.KeyboardButton(text="Ногти и здоровье🩺"),
            types.KeyboardButton(text="Модные тренды🔥"),
        ],
        [
            types.KeyboardButton(text="Записаться на процедуру🗓"),
            types.KeyboardButton(text="Цены и услуги💲"),
        ],
    ]

    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Обработка команды /start
@router.message(Command("start"))
async def handle_start(message: types.Message):
    """Обработка команды /start и отправка приветственного сообщения."""
    first_name = message.from_user.first_name
    greeting_text = format_greeting_message(first_name)
    markup = create_help_markup()
    await send_message_with_markup(message.chat.id, greeting_text, markup)

# Обработка команды /help некоммата лох
async def handle_help(message: types.Message):
    """Обработка команды /help и отправка сообщения помощи."""
    help_text = format_help_message()
    markup = create_help_markup()
    await send_message_with_markup(message.chat.id, help_text, markup)

# Создание разметки для выбора времени записи
def create_appointment_markup(dates, unavailable_time_slots):
    """Создание клавиатуры для выбора времени записи."""
    buttons = []
    
    # Генерация кнопок по датам и времени
    for date in dates:
        for time in range(16, 23, 2):  # Интервал 16:00-22:00 с шагом 2 часа
            if (date, time) not in unavailable_time_slots:
                button_text = f"{time}:00"
                callback_data = f"appointment_{date}_{time}"
                buttons.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    # Проверка, есть ли кнопки
    if buttons:
        # Создаем разметку с кнопками
        markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    else:
        # Если нет доступных интервалов времени, создаем разметку с одной кнопкой
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Нет доступных интервалов", callback_data="no_slots")]
        ])
    
    return markup



# Обработка текстовых сообщений для записи на процедуру
@router.message(lambda message: message.text.lower().startswith("записаться"))
async def handle_appointment_message(message: types.Message):
    """Обработка сообщения для записи на процедуру."""
    today = datetime.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    dates = [today, tomorrow]

    # Подключение к базе данных
    conn = sqlite3.connect("appointments.db")
    c = conn.cursor()

    # Получение существующих записей на сегодня и завтра
    c.execute("SELECT appointment_date, appointment_time FROM appointments WHERE appointment_date IN (?, ?)", (today, tomorrow))
    existing_appointments = c.fetchall()

    # Проверка существующих записей пользователя
    user_id = message.chat.id
    c.execute("SELECT * FROM appointments WHERE chat_id = ? AND appointment_date IN (?, ?)", (user_id, today, tomorrow))
    existing_user_appointments = c.fetchall()

    # Определение недоступных временных интервалов
    unavailable_time_slots = set()
    for appointment in existing_appointments:
        date, time = appointment
        unavailable_time_slots.add((date, time))

    if existing_user_appointments:
        for appointment in existing_user_appointments:
            date, time = appointment[1], appointment[2]
            unavailable_time_slots.add((date, time))

    # Создание клавиатуры для выбора времени
    markup = create_appointment_markup(dates, unavailable_time_slots)
    await send_message_with_markup(message.chat.id, "Выберите время для записи на процедуру:", markup)

    conn.close()

# Обработка колбеков для записи на процедуру
@router.callback_query(lambda callback: callback.data.startswith("appointment_"))
async def handle_appointment_callback(callback: types.CallbackQuery):
    """Обработка колбеков для записи на процедуру."""
    chat_id = callback.message.chat.id
    appointment_data = callback.data.split("_")
    date = appointment_data[1]
    appointment_time = int(appointment_data[2])

    # Внесение записи в базу данных
    conn = sqlite3.connect("appointments.db")
    c = conn.cursor()
    c.execute("INSERT INTO appointments (chat_id, appointment_date, appointment_time) VALUES (?, ?, ?)", 
              (chat_id, date, appointment_time))
    conn.commit()
    conn.close()

    await bot.send_message(chat_id, f"Вы выбрали {appointment_time}:00 для записи на процедуру в {date}.")

# Обработка текстовых сообщений
@router.message()
async def handle_text_message(message: types.Message):
    """Обработка текстовых сообщений и ответ на них."""
    response = get_response(message.text.lower().rstrip("💅📸💎💖🩺🔥🗓💲"))
    if callable(response):
        await response(message)
    else:
        await message.answer(response)

# Получение ответа на запрос пользователя
def get_response(message_text: str) -> str:
    """Получение соответствующего ответа в зависимости от ввода пользователя."""
    responses = {
        "хочу идеи для маникюра": "Here are some ideas for your manicure... 💅",
        "фотогалерея": "Check out our photo gallery... 📸",
        "тест": "Doing test... 💎",
        "советы по уходу": "Here are some care tips for your nails... 💖",
        "ногти и здоровье": "Learn how nail health affects your well-being... 🩺",
        "модные тренды": "Discover the latest manicure trends... 🔥",
        "цены и услуги": "Find out about our prices and services... 💲",
    }
    return responses.get(message_text, "Sorry, I don't understand that. Please try again.")

# Запуск бота
async def main():
    create_appointments_table()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
