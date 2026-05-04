import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from llm import llm_complete
from storage import save_schedule

scheduler = BackgroundScheduler()
scheduler.start()

STORAGE_FILE = "schedules.json"


# =========================
# Загрузка / сохранение
# =========================

def load_jobs():
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_jobs(jobs):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


# =========================
# Генерация поста
# =========================

def generate_post(topic, style):
    prompt = f"Тема: {topic}. Стиль: {style}. Сделай пост для путешественника."

    result = llm_complete(prompt, "Ты туристический ассистент")

    if not result:
        return f"📍 {topic}\n\nСоветы для путешествия."

    return result


# =========================
# Задача
# =========================

def job_function(bot, chat_id, topic, style):
    text = generate_post(topic, style)
    bot.send_message(chat_id, f"📅 Запланированный пост:\n\n{text}")


# =========================
# Добавление задачи
# =========================

def add_job(bot, chat_id, time_str, topic, style):

    hour, minute = map(int, time_str.split(":"))

    job = scheduler.add_job(
        job_function,
        "cron",
        hour=hour,
        minute=minute,
        args=[bot, chat_id, topic, style]
    )

    jobs = load_jobs()
    jobs.append({
        "id": job.id,
        "chat_id": chat_id,
        "time": time_str,
        "topic": topic,
        "style": style
    })

    save_schedule({
        "id": job.id,
        "chat_id": chat_id,
        "time": time_str,
        "topic": topic,
        "style": style
    })

    save_jobs(jobs)

    return job.id


# =========================
# Удаление задач пользователя
# =========================

def remove_user_jobs(chat_id):
    jobs = load_jobs()

    new_jobs = []

    for j in jobs:
        if j["chat_id"] == chat_id:
            try:
                scheduler.remove_job(j["id"])
            except:
                pass
        else:
            new_jobs.append(j)

    save_jobs(new_jobs)


# =========================
# Получить задачи
# =========================

def get_user_jobs(chat_id):
    jobs = load_jobs()
    return [j for j in jobs if j["chat_id"] == chat_id]