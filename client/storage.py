import json
from datetime import datetime

STORAGE_FILE = "storage.json"


# =========================
# БАЗОВЫЕ ФУНКЦИИ
# =========================

def load_data():
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "posts": [],
            "schedules": []
        }


def save_data(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# СОХРАНЕНИЕ ПОСТОВ
# =========================

def save_post(chat_id, text):
    data = load_data()

    data["posts"].append({
        "chat_id": chat_id,
        "text": text,
        "timestamp": datetime.now().isoformat()
    })

    save_data(data)


def get_posts(chat_id):
    data = load_data()
    return [p for p in data["posts"] if p["chat_id"] == chat_id]


# =========================
# СОХРАНЕНИЕ РАСПИСАНИЙ
# =========================

def save_schedule(job):
    data = load_data()
    data["schedules"].append(job)
    save_data(data)


def get_schedules(chat_id):
    data = load_data()
    return [j for j in data["schedules"] if j["chat_id"] == chat_id]


def clear_schedules(chat_id):
    data = load_data()
    data["schedules"] = [j for j in data["schedules"] if j["chat_id"] != chat_id]
    save_data(data)