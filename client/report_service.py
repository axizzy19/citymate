import requests

API_URL = "http://127.0.0.1:8000/country/"

def load_country(country):
    try:
        response = requests.get(API_URL + country, timeout=5)

        if response.status_code != 200:
            return None

        return response.json()

    except requests.exceptions.RequestException:
        return None


def analyze_country(data):

    population = data["population"]

    if population > 100_000_000:
        size = "очень крупная страна"
    elif population > 50_000_000:
        size = "крупная страна"
    elif population > 10_000_000:
        size = "средняя страна"
    else:
        size = "небольшая страна"

    metrics = {
        "size_category": size
    }

    return metrics


def format_report(data, metrics):

    report = f"""
📊 Мини-отчёт по стране

Страна: {data['name']}
Столица: {data['capital']}
Регион: {data['region']}
Население: {data['population']}

Ключевые показатели
• Категория по населению: {metrics['size_category']}

Наблюдения
• Страна расположена в регионе {data['region']}
• Столица является административным центром страны

Ограничения
• Данные получены из открытого API
• Возможны неточности или устаревшие сведения

⚠️ Дисклеймер
Данный ассистент предоставляет справочную информацию и не является официальным источником статистических данных.
"""

    return report