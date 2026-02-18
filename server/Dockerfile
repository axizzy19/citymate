# Используем Python, так как проект на нем написан [2]
FROM python:3.10-slim

WORKDIR /app

# Копируем зависимости (они должны быть в папке server)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из папки server в /app контейнера
COPY . .

# Порт, который слушает uvicorn
EXPOSE 8000

# Команда запуска (будет переопределена в docker-compose, но лучше иметь её и здесь)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]