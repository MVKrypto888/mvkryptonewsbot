import asyncio
import logging
import feedparser
from aiogram import Bot, Dispatcher, types, executor
from deep_translator import GoogleTranslator

# 🔧 Налаштування
BOT_TOKEN = '7977915751:AAG6lvmMAMOEAJmZAz5yARBYBth86F4TlUY'
RSS_URL = 'https://cointelegraph.com/rss'  # Cointelegraph
CHECK_INTERVAL = 60  # кожні 60 секунд

# 🔧 Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📍 Ініціалізація
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# 🧠 Зберігаємо останні ID новин
last_sent_links = set()
user_ids = set()

# 🔁 Переклад і форматування
def translate_and_trim(text):
    try:
        translated = GoogleTranslator(source='auto', target='ru').translate(text)
        return translated[:499]
    except Exception as e:
        logger.error(f"❌ Ошибка перевода: {e}")
        return text[:499]

def format_news(entry):
    title = translate_and_trim(entry.get("title", ""))
    summary = translate_and_trim(entry.get("summary", ""))
    return f"<b>{title}</b>\n\n{summary}"

# 🔁 Перевірка стрічки
async def check_feed():
    global last_sent_links
    while True:
        try:
            feed = feedparser.parse(RSS_URL)
            new_items = []
            for entry in feed.entries:
                if entry.link not in last_sent_links:
                    new_items.append(entry)
                    last_sent_links.add(entry.link)
            if new_items:
                for entry in reversed(new_items):
                    msg = format_news(entry)
                    for user_id in user_ids:
                        try:
                            await bot.send_message(chat_id=user_id, text=msg)
                        except Exception as e:
                            logger.error(f"❌ Ошибка при отправке: {e}")
            else:
                logger.info("ℹ️ Нет новых новостей.")
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке ленты: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

# 🟢 Команда /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_ids.add(message.chat.id)
    await message.reply("✅ Бот активирован. Вы будете получать все новости с Cointelegraph.")

# ▶️ Запуск
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_feed())
    executor.start_polling(dp, skip_updates=True)
