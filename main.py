import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from parser import parse_quotes
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import os

QUOTES_URL = "https://quotes.toscrape.com"
user_language : dict[int, str] = {}
user_topic : dict[int, str] = {}

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

CACHED_QUOTES = parse_quotes(QUOTES_URL)
TOPIC_CACHE: dict[str, list[dict]] = {}

def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Another quote", callback_data="get_quote")]
    ])
    return keyboard

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Russian", callback_data="ru")],
        [InlineKeyboardButton(text="English", callback_data="en")]
    ])
    return keyboard

TOPICS = ["love", "life", "inspirational", "humor", "success"]

def get_topics_keyboard():
    buttons = [
        [InlineKeyboardButton(text=topic.capitalize(), callback_data=f"topic_{topic}")]
        for topic in TOPICS
    ]
    buttons.append([InlineKeyboardButton(text="All topics", callback_data="topic_all")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def translate_text(text: str, target_text: str) -> str:
    if target_text == "en":
        return text
    elif target_text == "ru":
        try:
            return GoogleTranslator(source="en", target=target_text).translate(text)
        except Exception as e:
            print(f"Ошибка перевода: {e}")
            return text

def get_quotes_for_topic(topic: str) -> list[dict]:
    if topic == "all":
        return CACHED_QUOTES
    if topic not in TOPIC_CACHE:
        url = f"{QUOTES_URL}/tag/{topic}/"
        TOPIC_CACHE[topic] = parse_quotes(url)
    return TOPIC_CACHE[topic]

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        "Hello! I am topics-bot.\n\n"
        "Commands:\n"
        "/quotes — get random quotes\n"
        "/language — change language (RU/EN)\n"
        "/topics — change topics quotes")

@dp.message(Command('language'))
async def cmd_language(message: types.Message):
    await message.answer("Выберите язык:",reply_markup=get_language_keyboard())

def get_random_quote_text(user_id: int) -> str:
    topic = user_topic.get(user_id, "all")
    quotes = get_quotes_for_topic(topic)
    quote = random.choice(quotes)
    lang = user_language.get(user_id, "en")
    text = translate_text(quote["text"], lang)
    return f'{text}\n\n— {quote["author"]}\n\n🏷 {", ".join(quote["tags"])}'

@dp.message(Command('quotes'))
async def cmd_quotes(message: types.Message):
    text = get_random_quote_text(message.from_user.id)
    await message.answer(text, reply_markup=get_inline_keyboard())

@dp.message(Command('topics'))
async def cmd_topics(message: types.Message):
    await message.answer("Выбери тему:", reply_markup=get_topics_keyboard())

@dp.callback_query(lambda c: c.data.startswith("topic_"))
async def choice_topic(callback: types.CallbackQuery):
    await callback.answer()
    topic = callback.data.split("topic_")[1]
    user_topic[callback.from_user.id] = topic
    await callback.message.answer(f"Тема выбрана: {topic.upper()}")

@dp.callback_query(lambda c: c.data == "get_quote")
async def another_quote(callback: types.CallbackQuery):
    await callback.answer()
    text = get_random_quote_text(callback.from_user.id)
    await callback.message.answer(text, reply_markup=get_inline_keyboard())

@dp.callback_query(lambda c: c.data == "ru")
async def lang_ru(callback: types.CallbackQuery):
    await callback.answer()
    lang = callback.data
    user_language[callback.from_user.id] = lang
    await callback.message.answer(f"Язык установлен: {lang.upper()}")

@dp.callback_query(lambda c: c.data == "en")
async def lang_en(callback: types.CallbackQuery):
    await callback.answer()
    lang = callback.data
    user_language[callback.from_user.id] = lang
    await callback.message.answer(f"Language set to: {lang.upper()}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())