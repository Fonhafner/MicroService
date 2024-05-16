# Используем базовый образ Python
FROM python:3.9-slim AS base

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы с зависимостями
COPY requirements.txt .
COPY database_manager.py .

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y gcc
RUN pip install --no-cache-dir aiofiles
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn
RUN pip install python-keycloak

# Копируем файлы для сервиса micro
COPY Micro.py .
COPY static /app/static

# Копируем файлы для сервиса showusers
COPY showusers.py .
COPY templates /app/templates

# Устанавливаем переменные окружения
ENV DATABASE_URL=postgresql://postgres:yolo1204@87.242.119.51:5432/microbase

# Команды для запуска сервисов будут определены в docker-compose
