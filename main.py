import requests
from bs4 import BeautifulSoup
import sqlite3
import os
from tqdm import tqdm

# Tworzenie folderu na obrazki
os.makedirs("images", exist_ok=True)

# Połączenie z bazą danych
conn = sqlite3.connect("pytania.db")
cursor = conn.cursor()

# Tworzenie tabeli
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer_a TEXT,
    answer_b TEXT,
    answer_c TEXT,
    answer_d TEXT,
    correct_index INTEGER,
    image_path TEXT
)
""")

# Pobieranie strony
url = "https://www.praktycznyegzamin.pl/inf03ee09e14/teoria/wszystko/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Wszystkie pytania
question_divs = soup.find_all("div", class_="question")

# Pasek postępu
for q_div in tqdm(question_divs, desc="Przetwarzanie pytań"):
    title = q_div.find("div", class_="title").text.strip()
    answers = []
    correct = None

    for i, ans in enumerate(q_div.find_all("div", class_="answer")):
        text = ans.text.strip()
        answers.append(text)
        if "correct" in ans.get("class", []):
            correct = i

    # Obrazek
    image_url = None
    image_path = None
    img_tag = q_div.find("div", class_="image")
    if img_tag and img_tag.img:
        image_url = img_tag.img["src"]
        full_image_url = url + image_url
        image_name = image_url.split("/")[-1]
        image_path = os.path.join("images", image_name)

        # Pobieranie obrazka
        try:
            img_data = requests.get(full_image_url).content
            with open(image_path, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"Błąd pobierania obrazka: {image_url} → {e}")
            image_path = None

    # Zapis do bazy danych
    while len(answers) < 4:
        answers.append("")  # uzupełnij brakujące odpowiedzi

    cursor.execute("""
    INSERT INTO questions (question, answer_a, answer_b, answer_c, answer_d, correct_index, image_path)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, answers[0], answers[1], answers[2], answers[3], correct, image_path))

# Zapis i zamknięcie
conn.commit()
conn.close()
print("✅ Wszystkie pytania zostały zapisane do bazy danych.")
