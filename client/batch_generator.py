import time

def generate_batch(llm_func, topic, style, count, system_prompt):
    results = []

    for i in range(count):
        try:
            prompt = f"""
Тема: {topic}
Стиль: {style}

Сгенерируй туристическую рекомендацию #{i+1}.
"""

            response = llm_func(
                prompt,
                system_prompt,
                max_tokens=200
            )

            if response:
                results.append(f"--- Пост {i+1} ---\n{response}\n")
            else:
                results.append(f"--- Пост {i+1} ---\nОшибка генерации\n")

            time.sleep(1)

        except Exception as e:
            results.append(f"--- Пост {i+1} ---\nОшибка: {e}\n")

    return results


def save_to_txt(results, filename="batch.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    return filename