import requests
from bs4 import BeautifulSoup
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models
from tqdm import tqdm
import time

# Маппинг профилей
PROFILE_MODELS = {
    'e12': models.QuestionE12,
    'e13': models.QuestionE13,
    'ee08': models.QuestionINF02,
    'inf03ee09e14': models.QuestionINF03,
    'inf04': models.QuestionINF04
}

PROFILE_NAMES = {
    'e12': 'E.12',
    'e13': 'E.13',
    'ee08': 'INF.02',
    'inf03ee09e14': 'INF.03',
    'inf04': 'INF.04'
}

PROFILES_URLS = {
    'e12': 'https://www.praktycznyegzamin.pl/e12/teoria/wszystko/',
    'e13': 'https://www.praktycznyegzamin.pl/e13/teoria/wszystko/',
    'ee08': 'https://www.praktycznyegzamin.pl/ee08/teoria/wszystko/',
    'inf03ee09e14': 'https://www.praktycznyegzamin.pl/inf03ee09e14/teoria/wszystko/',
    'inf04': 'https://www.praktycznyegzamin.pl/inf04/teoria/wszystko/'
}

def download_image(image_url, profile_name, page_url):
    """Скачивает изображение"""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_dir = os.path.join(project_root, "static", "images", profile_name)
        os.makedirs(img_dir, exist_ok=True)
        
        # Формируем полный URL - ПРОСТО ДОБАВЛЯЕМ К page_url
        if image_url.startswith('http'):
            full_image_url = image_url
        else:
            # ВСЕ ИЗОБРАЖЕНИЯ относительно page_url
            full_image_url = page_url + image_url
        
        print(f"      → Полный URL: {full_image_url}")
        
        # Для имени файла убираем old/
        image_name = image_url.replace('old/', '').split("/")[-1]
        image_path = os.path.join(img_dir, image_name)
        
        # Если уже есть
        if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
            print(f"      → Уже существует локально")
            return f"/static/images/{profile_name}/{image_name}"
        
        # Скачиваем
        img_response = requests.get(full_image_url, timeout=10)
        img_response.raise_for_status()
        
        with open(image_path, "wb") as f:
            f.write(img_response.content)
        
        print(f"      → Сохранено в: {image_path}")
        
        # ВОЗВРАЩАЕМ ПУТЬ ДЛЯ БД (без old/)
        return f"/static/images/{profile_name}/{image_name}"
    
    except Exception as e:
        print(f"      ❌ Ошибка: {e}")
        return None

def parse_page(url, profile_name):
    """Парсит страницу"""
    print(f"\n🔍 Парсинг: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        question_divs = soup.find_all("div", class_="question")
        print(f"  📝 Найдено вопросов: {len(question_divs)}")
        
        if not question_divs:
            return []
        
        questions_data = []
        images_found = 0
        
        for q_div in question_divs:
            # Заголовок
            title_div = q_div.find("div", class_="title")
            if not title_div:
                continue
            
            title = title_div.text.strip()
            title = re.sub(r'^\d+\.\s*', '', title)
            
            # Ответы
            answers = []
            correct = None
            
            for i, ans in enumerate(q_div.find_all("div", class_="answer")):
                text = ans.text.strip()
                answers.append(text)
                if "correct" in ans.get("class", []):
                    correct = i
            
            while len(answers) < 4:
                answers.append("")
            
            clean_answers = []
            for ans in answers:
                clean = re.sub(r'^\s*[A-D]\.\s*', '', ans).strip()
                clean_answers.append(clean)
            
            correct_letter = chr(97 + correct) if correct is not None else None
            
            # Изображение - БЕЗ ФИЛЬТРА old/
            image_path = None
            img_tag = q_div.find("div", class_="image")
            
            if img_tag and img_tag.img:
                image_url = img_tag.img.get("src")
                
                if image_url:
                    print(f"    🖼️  Найдено изображение: {image_url}")
                    image_path = download_image(image_url, profile_name, url)
                    if image_path:
                        images_found += 1
                        print(f"    ✅ Скачано: {image_path}")
                    else:
                        print(f"    ❌ Не удалось скачать")
            
            if not title or correct_letter is None:
                continue
            
            questions_data.append({
                'question': title,
                'answer_a': clean_answers[0],
                'answer_b': clean_answers[1],
                'answer_c': clean_answers[2],
                'answer_d': clean_answers[3],
                'correct_answer': correct_letter,
                'image_url': image_path
            })
        
        print(f"  🖼️  Изображений найдено и скачано: {images_found}")
        
        return questions_data
    
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []
def scrape_profile(profile_key, base_url):
    """Парсит профиль"""
    model = PROFILE_MODELS.get(profile_key)
    profile_name = PROFILE_NAMES.get(profile_key)
    
    if not model:
        print(f"❌ Неизвестный профиль: {profile_key}")
        return
    
    print(f"\n{'='*60}")
    print(f"📚 {profile_name} → {model.__tablename__}")
    print(f"{'='*60}")
    
    questions_data = parse_page(base_url, profile_key)
    
    db = SessionLocal()
    added = 0
    updated = 0
    skipped = 0
    images = 0
    
    try:
        for q_data in tqdm(questions_data, desc="  💾 Сохранение"):
            existing = db.query(model).filter(
                model.question == q_data['question']
            ).first()
            
            if existing:
                # ОТЛАДКА
                print(f"\n    🔍 Найден существующий вопрос")
                print(f"    📝 Вопрос: {q_data['question'][:50]}...")
                print(f"    🖼️  Новое изображение: {q_data['image_url']}")
                print(f"    🖼️  Старое изображение: {existing.image_url}")
                
                # ОБНОВЛЯЕМ ЕСЛИ ЕСТЬ ИЗОБРАЖЕНИЕ
                if q_data['image_url'] and not existing.image_url:
                    existing.image_url = q_data['image_url']
                    updated += 1
                    images += 1
                    print(f"    ✅ ОБНОВЛЯЕМ!")
                else:
                    print(f"    ⏭️  Пропускаем")
                    if not q_data['image_url']:
                        print(f"       Причина: нет нового изображения")
                    if existing.image_url:
                        print(f"       Причина: уже есть изображение")
                    skipped += 1
                continue
            
            # ПРОВЕРЯЕМ ЧТО ПУТЬ К ИЗОБРАЖЕНИЮ ЕСТЬ
            if q_data['image_url']:
                images += 1
                print(f"\n    💾 Сохраняю с изображением: {q_data['image_url'][:50]}...")
            
            question = model(
                question=q_data['question'],
                answer_a=q_data['answer_a'],
                answer_b=q_data['answer_b'],
                answer_c=q_data['answer_c'],
                answer_d=q_data['answer_d'],
                correct_answer=q_data['correct_answer'],
                image_url=q_data['image_url'],
                explanation=""
            )
            
            db.add(question)
            added += 1
        
        db.commit()
        
        print(f"\n✅ Результат:")
        print(f"   📝 Всего добавлено: {added}")
        print(f"   🔄 Обновлено: {updated}")
        print(f"   🖼️  С изображениями: {images}")
        print(f"   ⏭️  Пропущено: {skipped}\n")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def main():
    print("\n🚀 СТАРТ ПАРСЕРА\n")
    
    # Создаем папки
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(project_root, "static", "images"), exist_ok=True)
    
    # Парсим все профили
    for profile_key, base_url in PROFILES_URLS.items():
        try:
            scrape_profile(profile_key, base_url)
            time.sleep(1)
        except Exception as e:
            print(f"❌ {profile_key}: {e}")
            continue
    
    print("🎉 ГОТОВО!\n")

if __name__ == "__main__":
    main()