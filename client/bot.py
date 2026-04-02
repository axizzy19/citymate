import os
import logging
import requests
from dotenv import load_dotenv
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from report_service import load_country, analyze_country, format_report, build_plot
from llm import llm_complete
from batch_generator import generate_batch, save_to_txt
from scheduler_service import add_job, get_user_jobs, remove_user_jobs
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

# ==============================
# Загрузка переменных окружения
# ==============================

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "http://localhost:8000"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}

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

        plot_path = build_plot(data)

        if plot_path:
            bot.send_photo(message.chat.id, open(plot_path, "rb"))

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

        try:
            bot.send_photo(message.chat.id, data['flag'], caption=text)
        except Exception:
            bot.send_message(message.chat.id, text + f"\n🏳 {data['flag']}")

    except Exception:
        bot.send_message(message.chat.id, "Ошибка подключения к серверу.")

@bot.message_handler(commands=['batch'])
def batch_handler(message):
    try:
        args = message.text.split()

        if len(args) < 4:
            bot.send_message(message.chat.id,
                "Использование: /batch <город> <стиль> <кол-во>\nПример: /batch paris guide 3")
            return

        topic = args[1]
        style = args[2]
        count = int(args[3])

        if count > 5:
            bot.send_message(message.chat.id, "Максимум 5 постов за раз.")
            return

        bot.send_message(message.chat.id, "Генерирую посты...")

        results = generate_batch(
            llm_complete,
            topic,
            style,
            count,
            SYSTEM_PROMPT
        )

        file_path = save_to_txt(results)

        bot.send_document(message.chat.id, open(file_path, "rb"))

        bot.send_message(message.chat.id, "Готово!")

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка batch-генерации.")

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
    if message.chat.id in user_states:
        return

    text = (
        "Чтобы помочь точнее, уточните:\n"
        "• Город\n"
        "• Тип места\n"
        "• Бюджет\n"
        "• Интересы"
    )
    bot.send_message(message.chat.id, text)

# ==============================
# Функця schedule
# ==============================

@bot.message_handler(commands=['schedule'])
def schedule_start(message):
    markup = InlineKeyboardMarkup()
    topics = ["Путешествие в Германию", "Путешествие в Италию", "Путешествие во Францию"]
    for t in topics:
        markup.add(InlineKeyboardButton(t, callback_data=f"topic|{t}"))

    user_states[message.chat.id] = {"step": "topic"}
    bot.send_message(message.chat.id, "Выберите тему путешествия:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    state = user_states.get(chat_id)

    if not state:
        bot.answer_callback_query(call.id)
        return

    # Выбор темы
    if state["step"] == "topic" and data.startswith("topic|"):
        topic = data.split("|")[1]
        state["topic"] = topic
        state["step"] = "style"

        # Кнопки для стиля
        markup = InlineKeyboardMarkup()
        styles = ["Кратко", "Блог", "Развернуто"]
        for s in styles:
            markup.add(InlineKeyboardButton(s, callback_data=f"style|{s}"))

        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=f"Тема выбрана: {topic}\nВыберите стиль:", reply_markup=markup)

    # Выбор стиля
    elif state["step"] == "style" and data.startswith("style|"):
        style = data.split("|")[1]
        state["style"] = style
        state["step"] = "time"

        # Кнопки времени (на ближайшие 3 минуты для теста)
        markup = InlineKeyboardMarkup()
        now = datetime.now()
        for i in range(1, 4):
            t = (now + timedelta(minutes=i)).strftime("%H:%M")
            markup.add(InlineKeyboardButton(t, callback_data=f"time|{t}"))

        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=f"Стиль выбран: {style}\nВыберите время для поста:", reply_markup=markup)

    # Выбор времени
    elif state["step"] == "time" and data.startswith("time|"):
        time_str = data.split("|")[1]
        state["time"] = time_str

        # Добавляем задачу в планировщик
        job_id = add_job(bot, chat_id, time_str, state["topic"], state["style"])
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=f"✅ Задача запланирована!\nID: {job_id}\nВремя: {time_str}\nТема: {state['topic']}\nСтиль: {state['style']}")

        # Удаляем состояние
        del user_states[chat_id]

    bot.answer_callback_query(call.id)

# ==============================
# Команда myschedule
# ==============================

@bot.message_handler(commands=['myschedule'])
def my_schedule(message):

    jobs = get_user_jobs(message.chat.id)

    if not jobs:
        bot.send_message(message.chat.id, "Нет активных задач")
        return

    text = "📅 Ваши задачи:\n\n"

    for j in jobs:
        text += f"ID: {j['id']}\n⏰ {j['time']}\n📌 {j['topic']} ({j['style']})\n\n"

    bot.send_message(message.chat.id, text)

# ==============================
# Команда stopall
# ==============================

@bot.message_handler(commands=['stopall'])
def stop_all(message):

    remove_user_jobs(message.chat.id)

    bot.send_message(message.chat.id, "🛑 Все задачи остановлены")

# ==============================
# Запуск
# ==============================

if __name__ == "__main__":
    logging.info("Бот запущен...")
    bot.remove_webhook()
    from scheduler_service import load_jobs, scheduler, job_function

    jobs = load_jobs()

    for j in jobs:
        hour, minute = map(int, j["time"].split(":"))

        scheduler.add_job(
            job_function,
            "cron",
            hour=hour,
            minute=minute,
            args=[bot, j["chat_id"], j["topic"], j["style"]],
            id=j["id"]
        )

    bot.infinity_polling()