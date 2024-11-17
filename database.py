import os
import mysql.connector
from dotenv import load_dotenv
import logging

logger = logging.getLogger("Database")

# Load environment variables
load_dotenv()

# Инициализация базы данных MySQL (подключение будет глобальным)
DB_HOST = os.getenv('MYSQLHOST')
DB_PORT = int(os.getenv("MYSQLPORT", 3306))
DB_USER = os.getenv('MYSQLUSER')
DB_PASSWORD = os.getenv('MYSQLPASSWORD')
DB_NAME = os.getenv('MYSQLDATABASE')

connection = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = connection.cursor()

# Текущая версия схемы базы данных
CURRENT_DB_VERSION = 2

# Скрипты обновлений
UPGRADE_SCRIPTS = {
    1: [
        """CREATE TABLE IF NOT EXISTS metadata (
               `key` VARCHAR(255) PRIMARY KEY,
               `value` TEXT NOT NULL
           )""",
        """INSERT INTO metadata (`key`, `value`) VALUES ('version', '1')""",
        """DROP TABLE events""",
        """DROP TABLE channels""",
        """DROP TABLE sent_events""",
    ],
    2: [
        """CREATE TABLE IF NOT EXISTS events (
            id VARCHAR(255) PRIMARY KEY,
            date DATETIME NOT NULL,
            message TEXT NOT NULL
            )""",
        """CREATE TABLE IF NOT EXISTS channels (
            id VARCHAR(255) PRIMARY KEY
            )""",
        """CREATE TABLE IF NOT EXISTS sent_events (
            event_id VARCHAR(255),
            channel_id VARCHAR(255),
            message_id INT,
            PRIMARY KEY (event_id, channel_id)
            )""",
    ]
}


def get_current_db_version(cursor):
    """
    Возвращает текущую версию базы данных из таблицы metadata.
    Если таблица или ключ отсутствуют, возвращает 0.
    """
    try:
        cursor.execute("SELECT `value` FROM metadata WHERE `key` = 'version'")
        result = cursor.fetchone()
        return int(result[0]) if result else 0
    except mysql.connector.errors.ProgrammingError:
        return 0


def apply_upgrade_scripts(cursor, from_version, to_version):
    """
    Применяет скрипты обновлений для базы данных от from_version до to_version.
    """
    for version in range(from_version + 1, to_version + 1):
        logger.info(f"Upgrading database to version {version}...")
        scripts = UPGRADE_SCRIPTS.get(version, [])
        for script in scripts:
            cursor.execute(script)
        logger.info(f"Database upgraded to version {version}.")


def update_db_version(cursor, new_version):
    """
    Обновляет версию базы данных в таблице metadata.
    """
    cursor.execute(
        "INSERT INTO metadata (`key`, `value`) VALUES ('version', %s) "
        "ON DUPLICATE KEY UPDATE `value` = VALUES(`value`)",
        (str(new_version),)
    )


"""
Инициализирует базу данных, обновляя её при необходимости.
"""
try:
    # Получение текущей версии базы данных
    current_version = get_current_db_version(cursor)
    logger.info(f"Current database version: {current_version}")

    # Обновление базы данных до текущей версии
    if current_version < CURRENT_DB_VERSION:
        apply_upgrade_scripts(cursor, current_version, CURRENT_DB_VERSION)
        update_db_version(cursor, CURRENT_DB_VERSION)
        connection.commit()
        logger.info(f"Database updated to version {CURRENT_DB_VERSION}.")
    else:
        logger.info("Database is already up-to-date.")
finally:
    cursor.close()
