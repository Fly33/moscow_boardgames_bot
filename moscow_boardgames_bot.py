import os
import telebot
import traceback
import time
import logging
from datetime import datetime, timedelta
from sources import rgub
from database import connection, cursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Логирование в файл
        logging.StreamHandler()         # Логирование в консоль
    ]
)

logger = logging.getLogger("TelegramBot")

sources = [
    rgub,
]

# Ваш токен бота и ID канала
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)


def register_channel(channel_id):
    cursor.execute("INSERT IGNORE INTO channels (id) VALUES (%s)", (channel_id,))
    connection.commit()

def unregister_channel(channel_id):
    cursor.execute("DELETE FROM channels WHERE id = %s", (channel_id,))
    connection.commit()

def is_event_sent(event_id, channel_id):
    cursor.execute("SELECT COUNT(*) FROM sent_events WHERE event_id = %s AND channel_id = %s", (event_id, channel_id))
    return cursor.fetchone()[0] > 0

def record_event_sent(event_id, channel_id, message_id):
    cursor.execute("INSERT INTO sent_events (event_id, channel_id, message_id) VALUES (%s, %s, %s)", 
                  (event_id, channel_id, message_id))
    connection.commit()

def get_registered_channels():
    """Возвращает список зарегистрированных каналов."""
    cursor.execute("SELECT id FROM channels")
    return [row[0] for row in cursor.fetchall()]


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработка команды /start."""
    bot.reply_to(message, f"Hello, {message.chat.first_name}!")


@bot.message_handler(commands=['register_channel'])
def handle_register_channel(message):
    """Обработка команды /register_channel <channel_id>."""
    try:
        channel_id = int(message.text.split()[1])
        register_channel(channel_id)
        bot.reply_to(message, f"Channel {channel_id} registered successfully.")
        handle_update(message)  # Запуск обновления
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /register_channel <channel_id>")


@bot.message_handler(commands=['unregister_channel'])
def handle_unregister_channel(message):
    """Обработка команды /unregister_channel <channel_id>."""
    try:
        channel_id = int(message.text.split()[1])
        unregister_channel(channel_id)
        bot.reply_to(message, f"Channel {channel_id} unregistered successfully.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /unregister_channel <channel_id>")


@bot.message_handler(commands=['update'])
def handle_update(message):
    """Обработка команды /update."""
    logger.info("Received /update command")
    
    try:
        # Источники событий
        events = []
        for source in sources:
            events_from_source = source.get_events()
            logger.info(f"Fetched {len(events_from_source)} events from {source.__class__.__name__}")
            events.extend(events_from_source)

        now = datetime.now()
        today_end = datetime.combine(now.date(), datetime.max.time())
        tomorrow_end = today_end + timedelta(days=1)

        # Добавление событий в таблицу `events`
        for event_id, event_date, event_message in events:
            cursor.execute(
                """
                INSERT IGNORE INTO events (id, date, message)
                VALUES (%s, %s, %s)
                """,
                (event_id, event_date, event_message)
            )
        connection.commit()
        logger.info("New events inserted into the database")

        # Выборка событий, которые:
        cursor.execute(
            """
            SELECT e.id, e.date, e.message
            FROM events e
            LEFT JOIN sent_events se ON e.id = se.event_id
            WHERE se.event_id IS NULL
              AND e.date BETWEEN %s AND %s
            """,
            (now, tomorrow_end)
        )
        pending_events = cursor.fetchall()
        logger.info(f"{len(pending_events)} pending events found")

        # Отправка сообщений пользователю
        for event_id, event_date, event_message in pending_events:
            for channel_id in get_registered_channels():
                try:
                    # Определяем дату отправки
                    send_date = event_date - timedelta(days=1)
                    if send_date <= now:
                        send_date = now

                    if send_date > now:
                        bot.send_message(
                            chat_id=channel_id,
                            text=f"Scheduled for {send_date.strftime('%Y-%m-%d %H:%M')}:\n{event_message}"
                        )
                        logger.info(f"Message scheduled for channel {channel_id}: {event_message}")
                    else:
                        sent_message = bot.send_message(
                            chat_id=channel_id,
                            text=event_message
                        )
                        record_event_sent(event_id, channel_id, sent_message.message_id)
                        logger.info(f"Message sent immediately to channel {channel_id}: {event_message}")
                except Exception as e:
                    logger.error(f"Error sending message to channel {channel_id}: {e}")

        bot.reply_to(message, "Update complete.")
        logger.info("Update command processed successfully")

    except Exception:
        logger.exception("Error processing /update command")
        bot.reply_to(message, "An error occurred while processing the update.")


if __name__ == '__main__':
    bot.remove_webhook()
    while True:
        try:
            bot.infinity_polling()
        except:
            traceback.print_exc()
        time.sleep(15)
