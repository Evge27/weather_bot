import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

TOKEN = "7568630701:AAFRGxeRjh-kVmpfWs34j6CsNWoxpqIZEuQ"
CHAT_ID = "5659803420"  # ID чата
WEATHER_API_KEY = "914e7cc21ac51e8250c9a536e56b9a50"
CITY = "Белград"

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()


# Функция для получения погоды по дням
async def get_weather_forecast(day: str, city=CITY):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang=ru&units=metric&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return "Город не найден, попробуйте ещё раз!"

        forecast_list = data["list"]
        today = datetime.date.today()

        if day == "today":
            target_date = today
            title = "сегодня"
        elif day == "tomorrow":
            target_date = today + datetime.timedelta(days=1)
            title = "завтра"
        elif day == "weekend":
            target_dates = {5: "Суббота", 6: "Воскресенье"}  # 5 = Суббота, 6 = Воскресенье
            weekend_forecast = {}

            for forecast in forecast_list:
                dt_txt = forecast["dt_txt"]
                forecast_date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()
                forecast_time = dt_txt[11:16]
                forecast_weekday = forecast_date.weekday()

                if forecast_weekday in target_dates and forecast_time in ["09:00", "12:00", "15:00"]:
                    weather_desc = forecast["weather"][0]["description"].capitalize()
                    temp = forecast["main"]["temp"]
                    wind = forecast["wind"]["speed"]

                    if forecast_date not in weekend_forecast:
                        weekend_forecast[forecast_date] = []

                    weekend_forecast[forecast_date].append(f"{forecast_time} - 🌡 {temp}°C, 💨 {wind} м/с, {weather_desc}")

            if not weekend_forecast:
                return "❌ Прогноз на выходные не найден."

            forecast_msg = f"🚨 <b>Выходные в {CITY}е</b>\n\n"
            for date, values in weekend_forecast.items():
                day_name = target_dates[date.weekday()]
                forecast_msg += f"<b>{day_name} ({date.strftime('%d.%m')}):</b>\n" + "\n".join(values) + "\n\n"

            return forecast_msg

        else:
            return "❌ Неверный день прогноза!"

        forecast_msg = f"🌤 <b>{CITY} {title} (09:00, 12:00, 15:00)</b>\n\n"
        for forecast in forecast_list:
            dt_txt = forecast["dt_txt"]
            forecast_date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()
            forecast_time = dt_txt[11:16]

            if forecast_date == target_date and forecast_time in ["09:00", "12:00", "15:00"]:
                weather_desc = forecast["weather"][0]["description"].capitalize()
                temp = forecast["main"]["temp"]
                wind = forecast["wind"]["speed"]

                forecast_msg += f"{forecast_time} - 🌡 {temp}°C, 💨 {wind} м/с, {weather_desc}\n"

        if "09:00" not in forecast_msg:
            return "❌ Прогноз не найден."

        return forecast_msg

    except Exception as e:
        print(f"Ошибка: {e}")
        return "Ошибка получения данных!"




# Функции обработки команд
@dp.message()
async def handle_commands(message: Message):
    if message.text == "/today":
        forecast = await get_weather_forecast("today")
        await message.reply(forecast, parse_mode="HTML")
    elif message.text == "/tomorrow":
        forecast = await get_weather_forecast("tomorrow")
        await message.reply(forecast, parse_mode="HTML")

    elif message.text == "/weekend":
        forecast = await get_weather_forecast("weekend")
        await message.reply(forecast, parse_mode="HTML")

    elif message.text == "/start":
        await message.reply("✅ Выберите, какой прогноз вам нужен:")


# Бот запускает прогноз автоматически без команды /start
async def send_weekend_forecast():
    forecast = await get_weather_forecast("weekend")
    await bot.send_message(CHAT_ID, forecast, parse_mode="HTML")

async def check_wind_alert():
    try:
        # Получаем прогноз погоды на несколько дней
        weather_data = await get_weather_forecast("today")  # Получаем прогноз на сегодня
        forecast_list = weather_data["list"]  # Прогноз на ближайшие несколько часов (каждый час)
        
        # Временные интервалы для проверки ветра
        time_intervals = ["03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
        
        # Пороговое значение для скорости ветра
        wind_threshold = 3  # Например, 5 м/с
        
        # Проверяем каждый прогноз на соответствующие временные интервалы
        for forecast in forecast_list:
            dt_txt = forecast["dt_txt"]  # Время прогноза
            forecast_time = dt_txt[11:16]  # Часы и минуты из времени прогноза (например, 03:00)

            # Если время совпадает с одним из нужных интервалов
            if forecast_time in time_intervals:
                wind_speed = forecast["wind"]["speed"]  # Скорость ветра в м/с

                # Если скорость ветра превышает порог
                if wind_speed > wind_threshold:
                    alert_message = f"🚨 <b> Внимание! Возможно Кошава!</b> Время: {forecast_time}. Скорость ветра: {wind_speed} м/с. Будьте осторожны!"
                    await bot.send_message(CHAT_ID, alert_message, parse_mode="HTML")
                    return  # Прерываем функцию, если одно из предупреждений уже отправлено
    except Exception as e:
        print(f"Ошибка при получении данных о ветре: {e}")

async def check_wind_alert_tomorrow():
    try:
        # Получаем прогноз погоды на завтра
        weather_data = await get_weather_forecast("tomorrow")  # Прогноз на завтра
        forecast_list = weather_data["list"]  # Данные с прогнозами на завтра
        
        # Временные интервалы для проверки ветра
        time_intervals = ["03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]
        
        # Пороговое значение для скорости ветра
        wind_threshold = 3  # Например, 5 м/с
        
        # Проверяем прогноз на завтра
        for forecast in forecast_list:
            dt_txt = forecast["dt_txt"]  # Время прогноза
            forecast_date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            forecast_time = dt_txt[11:16]  # Извлекаем только время (например, 03:00)

            # Проверяем, что прогноз относится именно к завтрашнему дню и нужному времени
            if forecast_date == tomorrow and forecast_time in time_intervals:
                wind_speed = forecast["wind"]["speed"]  # Скорость ветра в м/с

                # Если скорость ветра превышает порог
                if wind_speed > wind_threshold:
                    alert_message = f"🚨 <b> Внимание! Возможно Кошава завтра!</b> Время: {forecast_time}. Скорость ветра: {wind_speed} м/с. Будьте осторожны!"
                    await bot.send_message(CHAT_ID, alert_message, parse_mode="HTML")
                    return  # Прерываем функцию, если одно из предупреждений уже отправлено
    except Exception as e:
        print(f"Ошибка при получении данных о ветре на завтра: {e}")



async def main():
    print("Бот запущен!")

    # Автоматическая отправка прогноза каждую пятницу в 8:00
    scheduler.add_job(send_weekend_forecast, "cron", day_of_week="wed,fri", hour=8, minute=0, timezone="Europe/Belgrade")

    # Запускаем задачу каждый день в 07:00
    scheduler.add_job(check_wind_alert, "cron", hour=7, minute=0, timezone="Europe/Belgrade")

    # Запускаем задачу каждый день в 07:00
    scheduler.add_job(check_wind_alert_tomorrow, "cron", hour=12, minute=10, timezone="Europe/Belgrade")


    scheduler.start()
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
