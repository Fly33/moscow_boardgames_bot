import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Инициализация базы данных MySQL (подключение будет глобальным)
DB_HOST = os.getenv('MYSQLHOST')
DB_USER = os.getenv('MYSQLUSER')
DB_PASSWORD = os.getenv('MYSQLPASSWORD')
DB_NAME = os.getenv('MYSQLDATABASE')

print(f'''DB_HOST = {DB_HOST}
DB_USER = {DB_USER}
DB_PASSWORD = {DB_PASSWORD}
DB_NAME = {DB_NAME}''')


print("Environment variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = connection.cursor()

# Создание таблицы событий, если она еще не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INT PRIMARY KEY,
    date DATETIME NOT NULL,
    message TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    id INT PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sent_events (
    event_id INT,
    channel_id INT,
    message_id INT,
    PRIMARY KEY (event_id, channel_id)
)
""")
    
connection.commit()
