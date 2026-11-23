import asyncio
import requests
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os  # Встр библка для доступа к переменным сисмы
from dotenv import load_dotenv  # Функция загрузит данные из файла .env

#  Загружаем токен и айди из файла .env в память программы
load_dotenv()

# Достаем значения по их именам (os.getenv = "получить из окружения")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# Ссылка с фильтрами: ОЗУ, от 4 ГБ, сортировка по возр цены
URL = "https://catalog.onliner.by/sdapi/catalog.api/search/dram?order=price%3Aasc&volume_dram%5Bfrom%5D=4gb"


#  фя ищем самую дешев озу
def get_cheapest_ram():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Отправляем запрос и получаем JSON
    response = requests.get(URL, headers=headers)
    data = response.json()
    
    # Достаем список всех товаров
    products = data.get("products", [])
    
    # Перебираем товары по порядку (от самого дешевого к дорогому)
    for item in products:
        prices = item.get("prices")
        
        # Проверяем: если у товара есть блок prices и указана минимальная цена (значит он в наличии)
        if prices and prices.get("price_min"):
            name = item.get("full_name")
            link = item.get("html_url")
            price = prices["price_min"]["amount"]
            currency = prices["price_min"]["currency"]
            
            # Как только нашли первый доступный товар - сразу возвращаем результат и выходим из функции
            return (
                f" Самая дешевая ОЗУ (от 4 ГБ):\n"
                f" Модель: {name}\n"
                f" Цена: {price} {currency}\n"
                f" <a href='{link}'>Открыть на Onliner</a>"
            )
            
    return "Подходящих товаров в наличии не найдено."


# фя отправки соо
async def send_daily_message(bot: Bot):
    text = get_cheapest_ram()
    # Используем parse_mode="HTML", чтобы работало <a href> (ссылка)
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML")


# запуск по расписанию
async def main():
    bot = Bot(token=BOT_TOKEN)
    
    # Настройка таймер по минск вр
    scheduler = AsyncIOScheduler(timezone="Europe/Minsk")
    
    # Ставим будильник на каждый день
    scheduler.add_job(send_daily_message, trigger="cron", hour=22, minute=41, kwargs={"bot": bot})
    scheduler.start()
    
    print("Бот запущен! Ожидаю 22:41...")
    
    # Не даем скрипту завершиться
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":

    asyncio.run(main())

