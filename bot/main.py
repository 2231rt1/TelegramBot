import sqlite3
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import Router
from dotenv import load_dotenv


# Загрузка токена из .env файла
load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')

if TG_TOKEN is None:
    print("Токен бота не был загружен из файла .env")
    exit()

bot = Bot(token=TG_TOKEN)
# Инициализация бота
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
router = Router()

# Создание таблицы записей, если её нет
def create_appointments_table() -> None:
    """Создание таблицы для записей, если её нет."""
    with sqlite3.connect("appointments.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                chat_id INTEGER,
                appointment_date TEXT,
                appointment_time INTEGER
            )
        """)

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
        "* Видео галереям📸: Хочешь вдохновиться? Посмотри видео...\n"
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
        [types.KeyboardButton(text="Хочу идеи для маникюра💅"),
         types.KeyboardButton(text="Видеогалерея📹")],
        [types.KeyboardButton(text="Тест💎"),
         types.KeyboardButton(text="Советы по уходу💖")],
        [types.KeyboardButton(text="Ногти и здоровье🩺"),
         types.KeyboardButton(text="Модные тренды🔥")],
        [types.KeyboardButton(text="Записаться на процедуру🗓"),
         types.KeyboardButton(text="Цены и услуги💲")]
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

# Обработка команды /help
@router.message(Command("help"))
async def handle_help(message: types.Message):
    """Обработка команды /help и отправка сообщения помощи."""
    help_text = format_help_message()
    markup = create_help_markup()
    await send_message_with_markup(message.chat.id, help_text, markup)

# Обработка кнопку Видеогалеря
@router.message(lambda message: message.text.lower().startswith("видеогалерея"))
async def handle_video_gallery_message(message: types.Message):
    """Отправка видеороликов при нажатии на кнопку "Видеогалерея📹"."""
    video_dir = "videos"
    video_files = [
        "ArchedSquare.MOV",
        "Classik.MOV",
        "LongAlmond.MOV",
        "milk.MOV"
    ]
    for video_file in video_files:
        video_path = os.path.join(video_dir, video_file)
        await bot.send_video(message.chat.id, video=open(video_path, "rb"), caption="Видеогалерея")
    await send_message_with_markup(message.chat.id,"Так же вы можете просмотреть больше видеороликов и фото в нашем телеграм канале `ССЫЛКА`")

# Создание разметки для выбора времени записи
def create_appointment_markup(dates, unavailable_time_slots):
    buttons = [
        [InlineKeyboardButton(text=f"{time}:00", callback_data=f"appointment_{date}_{time}")]
        for date in dates
        for time in range(16, 23, 2)
        if (date, time) not in unavailable_time_slots
    ]

    # If no buttons are available, show a message
    if not buttons:
        buttons = [[InlineKeyboardButton(text="Нет доступных интервалов", callback_data="no_slots")]]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Обработка сообщений для записи на процедуру
@router.message(lambda message: message.text.lower().startswith("записаться"))
async def handle_appointment_message(message: types.Message):
    """Обработка сообщения для записи на процедуру."""
    today = datetime.today().strftime("%m-%d")
    dates = [(datetime.today() + timedelta(days=i)).strftime("%m-%d") for i in range(1)]  # На день вперед

    with sqlite3.connect("appointments.db") as conn:
        c = conn.cursor()
        # Получение существующих записей пользователя
        user_id = message.chat.id
        c.execute("SELECT appointment_date FROM appointments WHERE chat_id = ?", (user_id,))
        existing_user_appointments = c.fetchall()
        existing_user_dates = {appointment[0] for appointment in existing_user_appointments}

    # Определение недоступных временных интервалов
    unavailable_time_slots = {(date, time) for date in existing_user_dates for time in range(16, 23, 2)}

    # Проверка, есть ли у пользователя запись на сегодня
    c.execute("SELECT appointment_time FROM appointments WHERE chat_id = ? AND appointment_date = ?", (user_id, today))
    existing_today_appointments = c.fetchall()
    existing_today_times = {appointment[0] for appointment in existing_today_appointments}

    # Добавление временных слотов, которые уже заняты сегодня
    unavailable_time_slots.update((today, time) for time in existing_today_times)

    # Создание клавиатуры для выбора времени
    for date in dates:
        markup = create_appointment_markup([date], unavailable_time_slots)
        await bot.send_message(message.chat.id, f"Запись на {date}:")
        await send_message_with_markup(message.chat.id, "Выберите время для записи на процедуру:", markup)


# Обработка колбеков для записи на процедуру
@router.callback_query(lambda callback: callback.data.startswith("appointment_"))
async def handle_appointment_callback(callback: types.CallbackQuery):
    """Обработка колбеков для записи на процедуру."""
    chat_id = callback.message.chat.id
    date, appointment_time = callback.data.split("_")[1:3]

    # Проверка, есть ли у пользователя запись на этот день
    with sqlite3.connect("appointments.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM appointments WHERE chat_id = ? AND appointment_date = ?", (chat_id, date))
        existing_appointment = c.fetchone()

    if existing_appointment:
        await bot.send_message(chat_id, "Вы уже записаны на процедуру в этот день. Выберите другой день.")
        return

    # Внесение записи в базу данных
    with sqlite3.connect("appointments.db") as conn:
        conn.execute("INSERT INTO appointments (chat_id, appointment_date, appointment_time) VALUES (?, ?, ?)", 
                     (chat_id, date, int(appointment_time)))

    await bot.send_message(chat_id, f"Вы выбрали {appointment_time}:00 для записи на процедуру в {date}.")

# Обработка текстовых сообщений
@router.message()
async def handle_text_message(message: types.Message):
    """Обработка текстовых сообщений и ответ на них."""
    response = get_response(message.text.lower().rstrip("💅📸💎💖🩺🔥🗓💲"))
    await message.answer(response)

# Получение ответа на запрос пользователя
def get_response(message_text: str) -> str:
    """Получение соответствующего ответа в зависимости от ввода пользователя."""
    responses = {
        "хочу идеи для маникюра": "Вот несколько идей для вашего маникюра... 💅",
        "фотогалерея": "Посмотрите нашу фотогалерею... 📸",
        "тест": "Прохожу тест... 💎",
        "советы по уходу": "Вот несколько советов по уходу за ногтями... 💖",
        "ногти и здоровье": "Узнайте, как здоровье ногтей влияет на ваше самочувствие... 🩺",
        "модные тренды": "Откройте для себя последние тренды маникюра... 🔥",
        "цены и услуги": "Узнайте о наших ценах и услугах... 💲",
    }
    return responses.get(message_text, "Извините, я не понимаю. Пожалуйста, попробуйте снова.")

# Запуск бота
async def main():
    create_appointments_table()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
