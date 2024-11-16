# Используем минималистичный базовый образ Python
FROM python:3.11.6-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем проект в контейнер
COPY . /app

# Установка необходимых системных инструментов и локалей
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    && echo "ru_RU.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменные окружения для русской локали
ENV LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru \
    LC_ALL=ru_RU.UTF-8

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Настраиваем Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

CMD ["poetry", "run", "python", "main.py"]
