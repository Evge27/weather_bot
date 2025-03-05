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
@dp.message_handler()
async def get_weather(message: types.Message):
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=москва&lang=ru&units=metric&appid=your_token")
        data = response.json()
        city = data["name"]
        cur_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])

        # продолжительность дня
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) -       datetime.datetime.fromtimestamp(data["sys"]["sunrise"])

    except:
        await message.reply("Проверьте название города!")
