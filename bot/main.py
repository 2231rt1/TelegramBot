import os
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import Router
from dotenv import load_dotenv

# Load the bot token from .env file
load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')

if TG_TOKEN is None:
    print("Bot token not loaded from .env file")
    exit()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
router = Router()

# Database setup
def create_appointments_table() -> None:
    """Create appointments table if it doesn't exist."""
    with sqlite3.connect("appointments.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                chat_id INTEGER,
                appointment_date TEXT,
                appointment_time INTEGER
            )
        """)

# Message sending utility
async def send_message_with_markup(chat_id: int, text: str, markup: ReplyKeyboardMarkup) -> None:
    """Send a message with a keyboard markup."""
    await bot.send_message(chat_id, text, parse_mode='html', reply_markup=markup)

# Message formatting utilities
def format_greeting_message(first_name: str) -> str:
    return (f"Привет, {first_name}! Я твой помощник по маникюру! 💅\n"
            "С помощью меня ты можешь:\n\n"
            "* Посмотреть идеи для дизайна\n"
            "* Записаться на процедуру к мастеру\n"
            "* Получить советы по уходу за ногтями\n\n"
            "Напиши мне /help, чтобы узнать больше!")

def format_help_message() -> str:
    return ("Твой персональный эксперт по маникюру! ✨\n\n"
            "Просто напиши мне:\n\n"
            "* Хочу идеи для маникюра💅: Я покажу тебе самые модные дизайны...\n"
            "* Видео галереям📸: Хочешь вдохновиться? Посмотри видео...\n"
            "* Тест💎: Какой стиль маникюра тебе подходит?\n"
            "* Советы по уходу💖: Я поделюсь секретами ухода за ногтями...\n"
            "* Ногти и здоровье🩺: Узнай о здоровье ногтей...\n"
            "* Модные тренды🔥: Я расскажу о самых модных тенденциях...\n"
            "* Цены и услуги💲: Узнай больше о стоимости услуг...\n")

def create_help_markup() -> ReplyKeyboardMarkup:
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

# Command handlers
@router.message(Command("start"))
async def handle_start(message: types.Message):
    first_name = message.from_user.first_name
    greeting_text = format_greeting_message(first_name)
    markup = create_help_markup()
    await send_message_with_markup(message.chat.id, greeting_text, markup)

@router.message(Command("help"))
async def handle_help(message: types.Message):
    help_text = format_help_message()
    markup = create_help_markup()
    await send_message_with_markup(message.chat.id, help_text, markup)

@router.message(lambda message: message.text.lower().startswith("видеогалерея"))
async def handle_video_gallery_message(message: types.Message):
    video_dir = os.path.join(os.path.dirname(__file__), "videos")
    video_files = ["ArchedSquare.mp4", "Classik.mp4", "LongAlmond.mp4", "milk.mp4"]
    
    for video_file in video_files:
        video_path = os.path.join(video_dir, video_file)
        if os.path.exists(video_path):
            with open(video_path, 'rb') as file:
                await bot.send_video(message.chat.id, video=types.InputFile(file), caption="Видеогалерея")
        else:
            await bot.send_message(message.chat.id, f"Видео {video_file} не найдено.")
    
    await bot.send_message(message.chat.id, "Так же вы можете просмотреть больше видеороликов и фото в нашем телеграм канале `ССЫЛКА`")

# Appointment handling
def create_appointment_markup(dates, unavailable_time_slots):
    buttons = [
        [InlineKeyboardButton(text=f"{time}:00", callback_data=f"appointment_{date}_{time}")]
        for date in dates
        for time in range(16, 23, 2)
        if (date, time) not in unavailable_time_slots
    ]
    
    if not buttons:
        buttons = [[InlineKeyboardButton(text="Нет доступных интервалов", callback_data="no_slots")]]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(lambda message: message.text.lower().startswith("записаться"))
async def handle_appointment_message(message: types.Message):
    today = datetime.today().strftime("%m-%d")
    dates = [(datetime.today() + timedelta(days=i)).strftime("%m-%d") for i in range(1)]  # One day ahead

    with sqlite3.connect("appointments.db") as conn:
        c = conn.cursor()
        user_id = message.chat.id
        c.execute("SELECT appointment_date FROM appointments WHERE chat_id = ?", (user_id,))
        existing_user_dates = {appointment[0] for appointment in c.fetchall()}

        unavailable_time_slots = {(date, time) for date in existing_user_dates for time in range(15, 23, 3)}
        c.execute("SELECT appointment_time FROM appointments WHERE chat_id = ? AND appointment_date = ?", (user_id, today))
        existing_today_times = {appointment[0] for appointment in c.fetchall()}
        unavailable_time_slots.update((today, time) for time in existing_today_times)

    markup = create_appointment_markup(dates, unavailable_time_slots)
    await bot.send_message(message.chat.id, f"Запись на {today}:")
    await send_message_with_markup(message.chat.id, "Выберите время для записи на процедуру:", markup)

@router.callback_query(lambda callback: callback.data.startswith("appointment_"))
async def handle_appointment_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    date, appointment_time = callback.data.split("_")[1:3]

    with sqlite3.connect("appointments.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM appointments WHERE chat_id = ? AND appointment_date = ?", (chat_id, date))
        if c.fetchone():
            await bot.send_message(chat_id, "Вы уже записаны на процедуру в этот день. Выберите другой день.")
            return

        c.execute("INSERT INTO appointments (chat_id, appointment_date, appointment_time) VALUES (?, ?, ?)", 
                  (chat_id, date, int(appointment_time)))

    await bot.send_message(chat_id, f"Вы выбрали {appointment_time}:00 для записи на процедуру в {date}.")

@router.message()
async def handle_text_message(message: types.Message):
    response = get_response(message.text.lower().rstrip("💅📸💎💖🩺🔥🗓💲"))
    await message.answer(response)

def get_response(message_text: str) -> str:
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

# Start the bot
async def main():
    create_appointments_table()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
