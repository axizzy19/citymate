import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_complete(prompt, system_prompt, max_tokens=300, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    except Exception as e:
        print("LLM ERROR:", e)
        return generate_mock_response(prompt)

def generate_mock_response(prompt):
    return (
        "📍 Пример ответа (LLM недоступен, так как нет доступных токенов. Используется заглушка)\n\n"
        "1. Краткий ответ:\n"
        "Это демонстрационный ответ.\n\n"
        "2. Рекомендации:\n"
        "• Проверьте официальные сайты\n"
        "• Уточните расписание\n"
        "• Подготовьте документы\n\n"
        "⚠️ Данные могут быть неточными."
    )