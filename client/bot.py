import os
import logging
import requests
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from report_service import load_country, analyze_country, format_report
from llm import llm_complete

# ==============================
# Загрузка переменных окружения
# ==============================

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "http://localhost:8000"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = telebot.TeleBot(BOT_TOKEN)

# ==============================
# Логирование
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# Роль ассистента
# ==============================

ROLE_NAME = "CityMate"

ROLE_PROMPT = (
    "Ты дружелюбный попутчик. "
    "Отвечай кратко, структурированно, "
    "выделяй важные предупреждения."
)

DISCLAIMER = (
    "\n\n⚠️ Важно: всегда проверяйте актуальность информации "
    "на официальных источниках."
)

SYSTEM_PROMPT = """
Ты — туристический ассистент CityMate.

Отвечай кратко и структурированно.

Формат ответа:
1. Краткий ответ
2. Список рекомендаций
3. (если нужно) предупреждение

Не давай медицинских, юридических или финансовых советов.
"""
# ==============================
# Главное меню
# ==============================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("О боте"),
        KeyboardButton("Помощь")
    )
    markup.add(
        KeyboardButton("Что умею"),
        KeyboardButton("FAQ")
    )
    return markup

# ==============================
# Команды
# ==============================

@bot.message_handler(commands=["start"])
def start_handler(message):
    text = (
        f"Привет! Я {ROLE_NAME} 👋\n\n"
        "Я твой ассистент-путешественник.\n"
        "Помогу подготовиться к поездке и не потеряться в новом городе."
        + DISCLAIMER
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(commands=['ask'])
def ask(message):

    try:
        args = message.text.split(maxsplit=1)

        if len(args) < 2:
            bot.send_message(message.chat.id, "Использование: /ask ваш вопрос")
            return

        user_question = args[1]

        if len(user_question) > 500:
            bot.send_message(message.chat.id, "Слишком длинный запрос.")
            return

        prompt = f"Вопрос пользователя: {user_question}"

        response = llm_complete(
            prompt,
            SYSTEM_PROMPT,
            max_tokens=300,
            temperature=0.7
        )

        if not response:
            bot.send_message(message.chat.id, "Сервис временно недоступен.")
            return

        bot.send_message(message.chat.id, response)

    except Exception:
        bot.send_message(message.chat.id, "Ошибка обработки запроса.")


@bot.message_handler(commands=["help"])
def help_handler(message):
    text = (
        "📌 Доступные команды:\n"
        "/start — запуск\n"
        "/help — помощь\n"
        "/about — о боте\n"
        "/capabilities — что умею\n"
        "/faq — частые вопросы\n"
        "/ping — проверка связи\n"
        "/welcome <country> — приветственный пакет \n"
        "/report <country> — отчет о стране\n"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["about"])
def about_handler(message):
    text = (
        f"{ROLE_NAME} — интеллектуальный ассистент путешественника.\n\n"
        "Работает в онлайн- и офлайн-режиме.\n"
        "Сфокусирован на приватности данных."
        + DISCLAIMER
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["capabilities"])
def capabilities_handler(message):
    text = (
        "🧭 Я умею:\n"
        "• Подготовить Welcome Pack города\n"
        "• Подсказать, что уточнить перед поездкой\n"
        "• Помочь с базовой навигацией\n"
        "• Работать в режиме ассистента-попутчика"
        + DISCLAIMER
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["faq"])
def faq_handler(message):
    text = (
        "❓ FAQ\n\n"
        "Q: Работаешь без интернета?\n"
        "A: Критические функции работают офлайн.\n\n"
        "Q: Сохраняешь мои данные?\n"
        "A: Персональные данные не передаются без согласия."
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["ping"])
def ping_handler(message):
    bot.send_message(message.chat.id, "🏓 Pong! Бот работает.")

@bot.message_handler(commands=['report'])
def report(message):

    try:

        args = message.text.split()

        if len(args) < 2:
            bot.send_message(message.chat.id, "Использование: /report country")
            return

        country = args[1]

        data = load_country(country)

        if not data:
            bot.send_message(message.chat.id, "Ошибка получения данных.")
            return

        metrics = analyze_country(data)

        report = format_report(data, metrics)

        bot.send_message(message.chat.id, report)

    except Exception:
        bot.send_message(message.chat.id, "Ошибка формирования отчёта.")


@bot.message_handler(commands=["welcome"])
def welcome_handler(message):

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите страну: /welcome germany")
        return

    country = parts[1]

    try:
        response = requests.get(f"{API_URL}/country/{country}")

        if response.status_code != 200:
            bot.send_message(message.chat.id, "Не удалось получить данные.")
            return

        data = response.json()

        text = (
            f"🌍 Страна: {data['name']}\n"
            f"🏛 Столица: {data['capital']}\n"
            f"🌎 Регион: {data['region']}\n"
            f"👥 Население: {data['population']}\n"
            f"🏳 Флаг: {data['flag']}"
        )

        bot.send_message(message.chat.id, text)

    except Exception:
        bot.send_message(message.chat.id, "Ошибка подключения к серверу.")

# ==============================
# Кнопки меню
# ==============================

@bot.message_handler(func=lambda message: message.text == "О боте")
def about_button(message):
    about_handler(message)


@bot.message_handler(func=lambda message: message.text == "Помощь")
def help_button(message):
    help_handler(message)


@bot.message_handler(func=lambda message: message.text == "Что умею")
def capabilities_button(message):
    capabilities_handler(message)


@bot.message_handler(func=lambda message: message.text == "FAQ")
def faq_button(message):
    faq_handler(message)


# ==============================
# Что уточнить?
# ==============================

@bot.message_handler(func=lambda message: message.text.lower() in ["что уточнить?", "что спросить?"])
def clarify_handler(message):
    text = (
        "📝 Перед рекомендациями уточните:\n"
        "• Город\n"
        "• Бюджет\n"
        "• Интересы (музеи, еда, прогулки)\n"
        "• Длительность поездки\n"
        "• Язык\n"
        "• Нужен ли офлайн-режим"
    )
    bot.send_message(message.chat.id, text)


# ==============================
# Обработка свободного текста
# ==============================

@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    text = (
        "Чтобы помочь точнее, уточните:\n"
        "• Город\n"
        "• Тип места\n"
        "• Бюджет\n"
        "• Интересы"
    )
    bot.send_message(message.chat.id, text)


# ==============================
# Запуск
# ==============================

if __name__ == "__main__":
    logging.info("Бот запущен...")
    bot.remove_webhook()
    bot.infinity_polling()