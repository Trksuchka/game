# Используем официальный образ Python как базовый образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения в рабочую директорию
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY templates/ templates/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем команду для запуска приложения
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
