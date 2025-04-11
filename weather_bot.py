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
LAT = 44.49
LON = 20.28

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

def get_weather_emoji(weather_id: int) -> str:
    if 200 <= weather_id < 300:
        return "⛈"  # Гроза
    elif 300 <= weather_id < 400:
        return "🌦"  # Морось
    elif 500 <= weather_id < 600:
        return "🌧"  # Дождь
    elif 600 <= weather_id < 700:
        return "❄️"  # Снег
    elif 700 <= weather_id < 800:
        return "🌫"  # Туман, пыль, дымка🌫
    elif weather_id == 800:
        return "☀️"  # Ясно
    elif weather_id == 801:
        return "🌤"  # Малооблачно
    elif weather_id == 802:
        return "⛅️"  # Переменная облачность
    elif weather_id == 803:
        return "🌥"  # Облачно с прояснениями
    elif weather_id == 804:
        return "☁️"  # Пасмурно
    else:
        return "🌡"  # По умолчанию

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

        # Фильтруем прогноз на нужные дни
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

                if forecast_weekday in target_dates and forecast_time == "12:00":
                    weather_id = forecast["weather"][0]["id"]
                    emoji_main = get_weather_emoji(weather_id)

                if forecast_weekday in target_dates and forecast_time in ["09:00", "15:00", "21:00"]:
                    weather_desc = forecast["weather"][0]["description"].capitalize()
                    weather_id = forecast["weather"][0]["id"]
                    emoji = get_weather_emoji(weather_id)
                    temp = round(forecast["main"]["temp"],1)
                    wind_speed = forecast["wind"]["speed"]

                    if forecast_date not in weekend_forecast:
                        weekend_forecast[forecast_date] = []

                    weekend_forecast[forecast_date].append(f"{forecast_time} - 🌡 {temp}°C, 💨 {wind_speed} м/с, {emoji}{weather_desc}")
                    print(weather_id)


            if not weekend_forecast:
                return "❌ Прогноз на выходные не найден."

            forecast_msg = f" {emoji_main} <b>Выходные в {CITY}</b>\n\n"
            for date, values in weekend_forecast.items():
                day_name = target_dates[date.weekday()]
                forecast_msg += f"<b>{day_name} ({date.strftime('%d.%m')}):</b>\n" + "\n".join(values) + "\n\n"

            return forecast_msg

        else:
            return "❌ Неверный день прогноза!"

        forecast_msg = f" <b>{CITY} {title} </b>\n\n"

        # Ищем данные на 09:00, 12:00, 15:00, 18:00, 21:00
        for forecast in forecast_list:
            dt_txt = forecast["dt_txt"]
            forecast_date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()
            forecast_time = dt_txt[11:16]

            if forecast_date == target_date and forecast_time in ["09:00", "15:00", "21:00"]:
                weather_desc = forecast["weather"][0]["description"].capitalize()
                weather_id = forecast["weather"][0]["id"]
                emoji = get_weather_emoji(weather_id)
                temp = round(forecast["main"]["temp"],1)
                wind_speed = forecast["wind"]["speed"]

                forecast_msg += f"{forecast_time} - 🌡 {temp}°C, 💨 {wind_speed} м/с, {emoji}{weather_desc}\n"

        return forecast_msg

    except Exception as e:
        print(f"Ошибка: {e}")
        return "Ошибка получения данных!"

async def get_7_days_forecast():
    try:
        # API запрос для получения 7-дневного прогноза
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&lang=ru&units=metric&exclude=current,minutely,hourly&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "daily" not in data:
            return "Не удалось получить данные!"

        daily_forecast = data["daily"]  # Прогноз на каждый день
        forecast_msg = f"<b>Прогноз погоды на 7 дней в {CITY}</b>\n\n"

        for day_forecast in daily_forecast:
            date = datetime.datetime.utcfromtimestamp(day_forecast["dt"]).date()  # Получаем дату
            temp_day = round(day_forecast["temp"]["day"], 1)
            wind_speed = round(day_forecast["wind_speed"], 1)
            weather_desc = day_forecast["weather"][0]["description"].capitalize()
            weather_id = day_forecast["weather"][0]["id"]
            emoji = get_weather_emoji(weather_id)

            forecast_msg += f"{date} - 🌡 {temp_day}°C, 💨 {wind_speed} м/с, {emoji} {weather_desc}\n"

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

    elif message.text == "/5_days":
        forecast = await get_7_days_forecast()
        await message.reply(forecast, parse_mode="HTML")

    elif message.text == "/start":
        await message.reply("✅ Выберите, какой прогноз вам нужен:")


# Бот запускает прогноз автоматически без команды /start
async def send_weekend_forecast():
    forecast = await get_weather_forecast("weekend")
    await bot.send_message(CHAT_ID, forecast, parse_mode="HTML")


async def check_wind_speed_tomorrow(city=CITY):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang=ru&units=metric&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return print ("Город не найден, попробуйте ещё раз!")

        forecast_list = data["list"]
        today = datetime.date.today()
        target_date = today + datetime.timedelta(days=1)
        forecast_msg = ""
        print("Ветер на завтра")
        wind_exceeds_limit = False  # Флаг для проверки превышения ветра

        for forecast in forecast_list:
            dt_txt = forecast["dt_txt"]
            forecast_date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()
            forecast_time = dt_txt[11:16]

            if forecast_date == target_date and forecast_time in ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]:
                wind_speed = forecast["wind"]["speed"]

                if wind_speed > 5:
                    wind_exceeds_limit = True
                    weather_desc = forecast["weather"][0]["description"].capitalize()
                    weather_id = forecast["weather"][0]["id"]
                    emoji = get_weather_emoji(weather_id)
                    temp = round(forecast["main"]["temp"],1)

                    forecast_msg += f"{forecast_time} - 🌡 {temp}°C, 💨 {wind_speed} м/с, {emoji}{weather_desc}\n"

        if wind_exceeds_limit:
            forecast_msg = "🚨 Внимание! Завтра возможно Кошава!\n" + forecast_msg
            await bot.send_message(CHAT_ID, forecast_msg, parse_mode="HTML")

    except Exception as e:
        print(f"Ошибка: {e}")


async def check_wind_speed(city=CITY):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&lang=ru&units=metric&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return print ("Город не найден, попробуйте ещё раз!")

        forecast_list = data["list"]
        target_date = datetime.date.today()
        forecast_msg = ""
        print("Ветер на завтра")
        wind_exceeds_limit = False  # Флаг для проверки превышения ветра

        for forecast in forecast_list:
            dt_txt = forecast["dt_txt"]
            forecast_date = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").date()
            forecast_time = dt_txt[11:16]

            if forecast_date == target_date and forecast_time in ["06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]:
                wind_speed = forecast["wind"]["speed"]

                if wind_speed > 5:
                    wind_exceeds_limit = True
                    weather_desc = forecast["weather"][0]["description"].capitalize()
                    weather_id = forecast["weather"][0]["id"]
                    emoji = get_weather_emoji(weather_id)
                    temp = round(forecast["main"]["temp"],1)

                    forecast_msg += f"{forecast_time} - 🌡 {temp}°C, 💨 {wind_speed} м/с, {emoji}{weather_desc}\n"

        if wind_exceeds_limit:
            forecast_msg = "🚨 Внимание! Сегодня возможно Кошава!\n" + forecast_msg
            await bot.send_message(CHAT_ID, forecast_msg, parse_mode="HTML")

    except Exception as e:
        print(f"Ошибка: {e}")


async def main():
    print("Бот запущен!")

    # Автоматическая отправка прогноза каждую пятницу в 8:00
    scheduler.add_job(send_weekend_forecast, "cron", day_of_week="wed,fri", hour=8, minute=0,
                      timezone="Europe/Belgrade")

    # Проверим сегодня и завтра на превышение скорости ветра
    scheduler.add_job(check_wind_speed, "cron", hour=7, minute=0, timezone="Europe/Belgrade")
    scheduler.add_job(check_wind_speed_tomorrow, "cron", hour=7, minute=1, timezone="Europe/Belgrade")

    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
