FROM python:3.10-slim

WORKDIR /app

# Копируем файл зависимостей для клиента
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем код клиента (например, код телеграм-бота)
COPY . .

CMD ["python", "bot.py"]