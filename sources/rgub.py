import re
import requests
from datetime import datetime
import locale
from zoneinfo import ZoneInfo

# Добавляем временную зону
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

# Устанавливаем русскую локаль
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    print("Russian locale not available. Ensure it is installed on your system.")
    exit(1)


def escape(text):
    # Список символов Markdown, которые нужно экранировать
    escape_chars = r'_*~`#+|{}!'
    # Экранирование символов с помощью обратного слэша
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


# URL страницы
url = "https://rgub.ru/schedule/"

# Регулярное выражение
pattern = re.compile(
    r'<div[^>]*id="news(\d+)">\s*<div[^>]*>\s*<span[^>]*>(\d+)</span>/(\d+)<br\s*/>\s*'
    r'<span[^>]*>(\d+):(\d+)</span>\s*</div>\s*<!--DIV-->\s*<div[^>]*>\s*<p[^>]*>\s*'
    r'<a\s*href="([^"]+)"[^>]*>(Гик-зона|Играриум)</a>\s*</p>\s*</[^<]*<p>[^<]*<p>\s*'
    r'<p><a[^>]*>([^<]*)</a>\s*</p>\s*</div>\s*</div>'
)

# Словарь дней недели
days_of_week = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

def get_name():
    return "РГБМ"

def get_events():
    """
    Fetches the RGUB schedule page, extracts event data using regex,
    and returns a list of pairs (date, formatted_message).
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешность запроса
        content = response.text

        # Поиск всех совпадений
        matches = pattern.findall(content)

        # Список сообщений
        messages = []

        if matches:
            for match in matches:
                id, day, month, hour, minute, link, name, location = match
                id = "rgub" + id

                # Формируем дату
                date = datetime(
                    year=datetime.now().year, 
                    month=int(month), 
                    day=int(day), 
                    hour=int(hour), 
                    minute=int(minute),
                    tzinfo=MOSCOW_TZ
                )
                weekday = days_of_week[date.weekday()]

                # Форматируем дату и время
                formatted_date = f"{int(day)} {date.strftime('%B')}"
                time = f"{int(hour):02}:{int(minute):02}"

                # Формируем сообщение
                message = (
                    f"*{weekday}*\n\n"
                    "Российская государственная библиотека для молодежи\n"
                    "Адрес: ул. Б. Черкизовская, д 4 к 1\n"
                    "м. Преображенская площадь (вых.№5)\n\n"
                    f"{name}\n"
                    f"*{formatted_date} {time}*\n"
                    f"https://rgub.ru{escape(link)}\n\n"
                    f"{location}\n"
                    "Вход свободный\n"
                    "Возрастная категория 12\+\n"
                )

                # Добавляем пару (дата, сообщение) в список
                messages.append((id, date, message))

        return messages

    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []
