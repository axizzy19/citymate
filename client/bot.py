import os
import logging
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ==============================
# Загрузка переменных окружения
# ==============================

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
        "/welcome <город> — приветственный пакет"
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


@bot.message_handler(commands=["welcome"])
def welcome_handler(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите город: /welcome рим")
        return

    city = parts[1].capitalize()

    text = (
        f"🎒 Welcome Pack — {city}\n\n"
        "🚨 Экстренные номера: 112\n"
        "🚇 Транспорт из аэропорта: уточните заранее\n"
        "📜 Местные правила: уважайте культурные нормы\n"
        "🗺 Карта метро: сохраните офлайн заранее"
        + DISCLAIMER
    )

    bot.send_message(message.chat.id, text)

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
    bot.infinity_polling()