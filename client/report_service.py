import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

import pandas as pd
import matplotlib.pyplot as plt


def build_plot(main_country_data):
    try:
        countries = ["germany", "france", "italy", "spain", "netherlands"]

        rows = []

        for c in countries:
            try:
                resp = requests.get(f"https://restcountries.com/v3.1/name/{c}")
                if resp.status_code != 200:
                    continue

                country_data = resp.json()[0]

                rows.append({
                    "country": country_data.get("name", {}).get("common", c),
                    "population": country_data.get("population", 0)
                })

            except:
                continue

        rows.append({
            "country": main_country_data.get("name", "Selected"),
            "population": main_country_data.get("population", 0)
        })

        df = pd.DataFrame(rows)

        df = df.sort_values(by="population", ascending=False)

        plt.figure()

        plt.bar(df["country"], df["population"])

        plt.title("Population Comparison")
        plt.xlabel("Country")
        plt.ylabel("Population")
        plt.xticks(rotation=30)

        filename = "plot.png"
        plt.savefig(filename)
        plt.close()

        return filename

    except Exception as e:
        print("PLOT ERROR:", e)
        return None