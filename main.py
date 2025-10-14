import requests
from bs4 import BeautifulSoup
import sqlite3
import os
from tqdm import tqdm
import uuid

# Список профилей и их базовые URL
profiles_urls = {
    'e13': 'https://www.praktycznyegzamin.pl/e13',
    'ee08': 'https://www.praktycznyegzamin.pl/ee08',
    'inf03ee09e14': 'https://www.praktycznyegzamin.pl/inf03ee09e14',
    'inf04': 'https://www.praktycznyegzamin.pl/inf04',
    'e12': 'https://www.praktycznyegzamin.pl/e12'
}

# Подключение к базе данных
conn = sqlite3.connect("pytania.db")
cursor = conn.cursor()

# Создание таблиц для каждого профиля
for profile in profiles_urls.keys():
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {profile} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer_a TEXT,
            answer_b TEXT,
            answer_c TEXT,
            answer_d TEXT,
            correct_index INTEGER,
            image_path TEXT
        )
    """)
conn.commit()

# Функция для парсинга и вставки вопросов
def parse_and_insert(url_base, profile_name):
    # Создать папку для изображений профиля (изменено на "photo")
    img_dir = os.path.join("photo", profile_name)
    os.makedirs(img_dir, exist_ok=True)
    
    # URL страницы с вопросами (с /teoria/wszystko/)
    url = f"{url_base}/teoria/wszystko/"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка при загрузке страницы {url}: {e}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    question_divs = soup.find_all("div", class_="question")
    
    # Проверка на наличие вопросов
    if not question_divs:
        print(f"Вопросы не найдены на странице {url}")
        return
    
    # Обработка вопросов с прогресс-баром
    for q_div in tqdm(question_divs, desc=f"Обработка вопросов для {profile_name}"):
        title = q_div.find("div", class_="title")
        if not title:
            print("Вопрос без заголовка, пропускаем")
            continue
        title = title.text.strip()
        
        answers = []
        correct = None
        for i, ans in enumerate(q_div.find_all("div", class_="answer")):
            text = ans.text.strip()
            answers.append(text)
            if "correct" in ans.get("class", []):
                correct = i
        
        # Обработка изображения
        image_path = None
        img_tag = q_div.find("div", class_="image")
        if img_tag and img_tag.img:
            image_url = img_tag.img["src"]
            full_image_url = image_url if image_url.startswith('http') else url + image_url
            image_name = os.path.basename(image_url)
            image_path = os.path.join(img_dir, image_name)
            try:
                img_data = requests.get(full_image_url).content
                with open(image_path, "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print(f"Ошибка загрузки изображения {full_image_url}: {e}")
                image_path = None
        
        # Дополнить ответы, если их меньше 4
        while len(answers) < 4:
            answers.append("")
        
        # Вставка в таблицу профиля
        cursor.execute(f"""
            INSERT INTO {profile_name} (question, answer_a, answer_b, answer_c, answer_d, correct_index, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, answers[0], answers[1], answers[2], answers[3], correct, image_path))
    
    conn.commit()
    print(f"✅ Вопросы для профиля {profile_name} успешно добавлены.")

# Парсинг для каждого профиля
for profile, base_url in profiles_urls.items():
    parse_and_insert(base_url, profile)

# Закрытие соединения с БД
conn.close()
print("Все профили обработаны.")