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
async def get_weather(message: types.Message):
    city = message.text.strip()  # Получаем текст сообщения (название города)
    
    if not city:
        await message.reply("Введите название города!")
        return

    try:
        # Запрос к OpenWeather API
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid={WEATHER_API_KEY}"
        )
        data = response.json()

        if data.get("cod") != 200:
            await message.reply("Город не найден, попробуйте еще раз!")
            return

        # Извлекаем данные
        city_name = data["name"]
        cur_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = sunset_timestamp - sunrise_timestamp

        # Формируем ответ
        weather_info = (
            f"Погода в городе **{city_name}**:\n"
            f"🌡 Температура: {cur_temp}°C\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌬 Ветер: {wind} м/с\n"
            f"🌀 Давление: {pressure} мм рт. ст.\n"
            f"🌅 Восход: {sunrise_timestamp.strftime('%H:%M:%S')}\n"
            f"🌇 Закат: {sunset_timestamp.strftime('%H:%M:%S')}\n"
            f"⏳ Продолжительность дня: {length_of_the_day}"
        )

        await message.reply(weather_info, parse_mode="Markdown")

    except Exception as e:
        await message.reply("Ошибка получения данных. Проверьте название города!")
        print(f"Ошибка: {e}")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
