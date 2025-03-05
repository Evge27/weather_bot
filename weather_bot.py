import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

TOKEN = "7568630701:AAFRGxeRjh-kVmpfWs34j6CsNWoxpqIZEuQ"
CHAT_ID = "5659803420"  # ID чата, куда отправлять сообщения
WEATHER_API_KEY = "914e7cc21ac51e8250c9a536e56b9a50"
CITY = "Белград"

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Функция получения прогноза на указанные часы (09:00, 12:00, 15:00)
async def get_weekend_forecast(city=CITY, times=["09:00", "12:00", "15:00"]):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang=ru&units=metric&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return "Город не найден, попробуйте ещё раз!"

        forecast_list = data["list"]

        # Определяем ближайшие выходные (суббота и воскресенье)
        days_ahead = {5: "Суббота", 6: "Воскресенье"}  # 5 = Суббота, 6 = Воскресенье
        weekend_forecast = {5: {}, 6: {}}  # Храним прогноз отдельно для каждого дня

        for forecast in forecast_list:
            dt_txt = forecast["dt_txt"]  # Формат: '2024-03-09 09:00:00'
            forecast_date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()
            forecast_time = dt_txt[11:16]  # Берем только время (HH:MM)
            forecast_weekday = forecast_date.weekday()

            # Фильтруем только субботу и воскресенье в нужное время
            if forecast_weekday in days_ahead and forecast_time in times:
                weather_desc = forecast["weather"][0]["description"].capitalize()
                temp = forecast["main"]["temp"]
                wind = forecast["wind"]["speed"]

                weekend_forecast[forecast_weekday][forecast_time] = (
                    f"🌡 {temp}°C, 💨 {wind} м/с, {weather_desc} ({forecast_time})"
                )

        # Формируем сообщение
        if not weekend_forecast[5] and not weekend_forecast[6]:
            return "❌ Прогноз на выходные не найден."

        forecast_msg = f"🌤 <b>Прогноз на выходные в {CITY}</b>\n\n"
        for day in [5, 6]:  # Суббота и Воскресенье
            if weekend_forecast[day]:
                forecast_msg += f"<b>{days_ahead[day]}:</b>\n"
                for time, values in weekend_forecast[day].items():
                    forecast_msg += f"{values}\n"
                forecast_msg += "\n"

        return forecast_msg

    except Exception as e:
        print(f"Ошибка: {e}")
        return "Ошибка получения данных!"


# Функция отправки прогноза
async def send_weekend_forecast():
    forecast = await get_weekend_forecast()
    await bot.send_message(CHAT_ID, forecast, parse_mode="HTML")


# Автоматическое расписание (отправка прогноза)
def setup_scheduler():
    scheduler.remove_all_jobs()

    # Отправка прогноза в пятницу в 18:00
    scheduler.add_job(send_weekend_forecast, "cron", day_of_week="thu", hour=10, minute=0, timezone="Europe/Belgrade")

    scheduler.start()


# Запуск бота
async def main():
    print("Бот запущен!")
    setup_scheduler()  # Автоматически включаем расписание
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
