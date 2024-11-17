import os
import mysql.connector
from dotenv import load_dotenv

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

# Создание таблицы событий, если она еще не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(255) PRIMARY KEY,
    date DATETIME NOT NULL,
    message TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    id VARCHAR(255) PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sent_events (
    event_id VARCHAR(255),
    channel_id VARCHAR(255),
    message_id INT,
    PRIMARY KEY (event_id, channel_id)
)
""")
    
connection.commit()
