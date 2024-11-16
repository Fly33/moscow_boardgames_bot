FROM python:3.11.6-slim

WORKDIR /app
COPY . /app

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Установите русскую локаль
RUN apt-get update && apt-get install -y locales \
    && locale-gen ru_RU.UTF-8

# Устанавливаем переменные окружения для Python
ENV LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru \
    LC_ALL=ru_RU.UTF-8

CMD ["poetry", "run", "python", "main.py"]
