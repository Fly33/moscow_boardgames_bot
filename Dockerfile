# Используем официальный образ Python
FROM python:3.11.6-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем содержимое проекта
COPY . /app

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Конфигурация Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Установка локалей и настройка русской локали
RUN apt-get update && apt-get install -y --no-install-recommends locales \
    && locale-gen ru_RU.UTF-8 \
    && update-locale LANG=ru_RU.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменные окружения для Python
ENV LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru \
    LC_ALL=ru_RU.UTF-8

CMD ["poetry", "run", "python", "main.py"]
