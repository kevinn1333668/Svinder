# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src /app/src

# Запускаем приложение
WORKDIR /app
CMD ["python", "-m", "src.main"]