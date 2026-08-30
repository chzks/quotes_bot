import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from parser import parse_quotes
from dotenv import load_dotenv
import os

QUOTES_URL = "https://quotes.toscrape.com"

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Another quote", callback_data="get_quote")]
    ])
    return keyboard

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer("Hello, enter: '/quotes' for Quotes")

def get_random_quote_text() -> str:
    quotes = parse_quotes(QUOTES_URL)
    quote = random.choice(quotes)
    return f'{quote["text"]}\n\n— {quote["author"]}\n\n🏷 {", ".join(quote["tags"])}'

@dp.message(Command('quotes'))
async def cmd_quotes(message: types.Message):
    text = get_random_quote_text()
    await message.answer(text, reply_markup=get_inline_keyboard())


@dp.callback_query(lambda c: c.data == "get_quote")
async def another_quote(callback: types.CallbackQuery):
    await callback.answer()
    text = get_random_quote_text()
    await callback.message.answer(text, reply_markup=get_inline_keyboard())


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())