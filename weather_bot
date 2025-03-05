import asyncio
import datetime
import requests
from aiogram import Bot, Dispatcher, types

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

DEFAULT_CITY = "Белград"

# Функция для получения текущей погоды
async def get_current_weather(city: str):
    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid={WEATHER_API_KEY}"
        )
        data = response.json()

        if data.get("cod") != 200:
            return "Город не найден, попробуйте ещё раз!"

        city_name = data["name"]
        cur_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = sunset_timestamp - sunrise_timestamp

        return (
            f"🌍 Погода в **{city_name}**:\n"
            f"🌡 Температура: *{cur_temp}*°C\n"
            f"💧 Влажность: *{humidity}*%\n"
            f"🌬 Ветер: *{wind}* м/с\n"
            f"🌀 Давление: *{pressure}* мм рт. ст.\n"
            f"🌅 Восход: {sunrise_timestamp.strftime('%H:%M:%S')}\n"
            f"🌇 Закат: {sunset_timestamp.strftime('%H:%M:%S')}\n"
            f"⏳ Продолжительность дня: {length_of_the_day}"
        )

    except Exception as e:
        print(f"Ошибка: {e}")
        return "Ошибка получения данных. Проверьте название города!"

# Функция для получения погоды на ближайшие выходные
async def get_weekend_forecast(city: str):
    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang=ru&units=metric&appid={WEATHER_API_KEY}"
        )
        data = response.json()

        if data.get("cod") != "200":
            return "Город не найден, попробуйте ещё раз!"

        forecast_message = f"📅 Прогноз погоды в **{city}** на ближайшие выходные:\n\n"
        weekend_days = []

        # Получаем ближайшие субботу и воскресенье
        today = datetime.datetime.today().date()
        for i in range(1, 7):  # Проверяем ближайшие 7 дней
            check_date = today + datetime.timedelta(days=i)
            if check_date.weekday() in [5, 6]:  # 5 - суббота, 6 - воскресенье
                weekend_days.append(check_date)

        # Фильтруем прогноз по выходным
        for forecast in data["list"]:
            forecast_time = datetime.datetime.fromtimestamp(forecast["dt"])
            forecast_date = forecast_time.date()
            if forecast_date in weekend_days:
                temp = forecast["main"]["temp"]
                wind = forecast["wind"]["speed"]
                description = forecast["weather"][0]["description"].capitalize()
                forecast_message += (
                    f"📆 *{forecast_date.strftime('%d.%m.%Y')}* в {forecast_time.strftime('%H:%M')}:\n"
                    f"🌡 *{temp}*°C, {description}\n"
                    f"🌬 Ветер: *{wind}* м/с\n\n"
                )

        return forecast_message

    except Exception as e:
        print(f"Ошибка: {e}")
        return "Ошибка получения прогноза!"

# Команда /start – отправляет прогноз на ближайшие выходные
@dp.message()
async def start_command(message: types.Message):
    if message.text == "/start":
        weather_forecast = await get_weekend_forecast(DEFAULT_CITY)
        await message.reply(weather_forecast, parse_mode="MarkdownV2")
    else:
        city = message.text.strip() or DEFAULT_CITY
        weather_info = await get_current_weather(city)
        await message.reply(weather_info, parse_mode="MarkdownV2")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
