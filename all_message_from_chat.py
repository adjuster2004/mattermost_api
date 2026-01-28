import requests

# --- КОНФИГУРАЦИЯ ---
SERVER_URL = "https://chat.yourcompany.com" # ВАШ URL (без слэша в конце)
CHANNEL_ID = "здесь_ваш_id_канала"
MANUAL_TOKEN = "вставьте_сюда_скопированный_токен"
OUTPUT_FILE = "mattermost_text_only.txt"

def fetch_messages(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    messages = []
    page = 0
    per_page = 60

    print(f"Подключаюсь к {SERVER_URL}...")

    while True:
        url = f"{SERVER_URL}/api/v4/channels/{CHANNEL_ID}/posts"
        params = {"page": page, "per_page": per_page}

        try:
            resp = requests.get(url, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            break

        if resp.status_code == 401:
            print("Ошибка: Токен просрочен.")
            break
        elif resp.status_code != 200:
            print(f"Ошибка сервера: {resp.status_code}")
            break

        data = resp.json()
        posts = data.get("posts", {})
        order = data.get("order", [])

        if not order:
            print("Сообщения закончились.")
            break

        print(f"Обрабатываю страницу {page}... (в пачке {len(order)} записей)")

        for post_id in order:
            post = posts[post_id]

            # 1. Пропускаем системные сообщения
            post_type = post.get("type", "")
            if post_type.startswith("system_"):
                continue

            text = post.get("message", "")

            # 2. Если текст есть, сохраняем ТОЛЬКО его
            if text:
                # Заменяем переносы строк внутри сообщения на пробелы,
                # чтобы структура файла была линейной.
                clean_text = text.replace('\n', ' ')

                # Добавляем в список только текст, без даты и автора
                messages.append(clean_text)

        page += 1

    return messages

# --- ЗАПУСК ---
if __name__ == "__main__":
    if len(MANUAL_TOKEN) < 10:
        print("Вставьте токен в скрипт!")
    else:
        history = fetch_messages(MANUAL_TOKEN)
        if history:
            print(f"Найдено сообщений: {len(history)}")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                # reversed нужен, чтобы сообщения шли в хронологическом порядке (от старых к новым)
                for line in reversed(history):
                    f.write(line + "\n")
            print(f"Готово. Файл: {OUTPUT_FILE}")
