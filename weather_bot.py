import asyncio
import os
import datetime
import requests
from aiogram import Bot, Dispatcher, types

# Укажите токен бота
TOKEN = "7568630701:AAFRGxeRjh-kVmpfWs34j6CsNWoxpqIZEuQ"

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хэндлер команды /start
@dp.message()
async def start_command(message: types.Message):
    if message.text == "/start":
        await message.reply("Привет! Напиши мне название города, и я пришлю сводку погоды")

async def main():
    # Запуск поллинга
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
