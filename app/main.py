from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import or_
import random
import os

from .database import get_db, Base, engine
from . import models, schemas

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WEB3Informatyk API")

PRACTICE_DIR = Path("downloaded_practice")
if PRACTICE_DIR.exists():
    app.mount("/practice", StaticFiles(directory=str(PRACTICE_DIR)), name="practice")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web-informatyk.lol", "https://www.web-informatyk.lol"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Маппинг категорий на модели таблиц
CATEGORY_MODELS = {
    "E.12": models.QuestionE12,
    "E.13": models.QuestionE13,
    "INF.02": models.QuestionINF02,
    "INF.03": models.QuestionINF03,
    "INF.04": models.QuestionINF04,
}

PRACTICE_MODELS = {
    'inf02': models.PracticeINF02,
    'ee08': models.PracticeEE08,
    'e12': models.PracticeE12,
    'e13': models.PracticeE13,
    'inf03': models.PracticeINF03,
    'ee09': models.PracticeEE09,
    'e14': models.PracticeE14,
    'inf04': models.PracticeINF04,
}

PRACTICE_PROFILES_INFO = {
    'inf02': {
        'id': 'inf02',
        'name': 'INF.02',
        'title': 'Administracja systemami komputerowymi',
        'icon': '🖥️',
        'color': '#667eea',
        'category': 'Technik informatyk',
        'description': 'Administracja i eksploatacja systemów komputerowych, urządzeń peryferyjnych i lokalnych sieci komputerowych'
    },
    'ee08': {
        'id': 'ee08',
        'name': 'EE.08',
        'title': 'Montaż i eksploatacja systemów komputerowych',
        'icon': '🔧',
        'color': '#f59e0b',
        'category': 'Technik informatyk (stara podstawa)',
        'description': 'Montaż, uruchamianie i konserwacja komputerów oraz urządzeń peryferyjnych'
    },
    'e12': {
        'id': 'e12',
        'name': 'E.12',
        'title': 'Montaż i eksploatacja komputerów osobistych',
        'icon': '💻',
        'color': '#06b6d4',
        'category': 'Technik informatyk (bardzo stara podstawa)',
        'description': 'Montaż komputerów osobistych oraz instalacja systemów i programów użytkowych'
    },
    'e13': {
        'id': 'e13',
        'name': 'E.13',
        'title': 'Projektowanie lokalnych sieci komputerowych',
        'icon': '🌐',
        'color': '#8b5cf6',
        'category': 'Technik informatyk (bardzo stara podstawa)',
        'description': 'Projektowanie lokalnych sieci komputerowych i administrowanie sieciami'
    },
    'inf03': {
        'id': 'inf03',
        'name': 'INF.03',
        'title': 'Tworzenie i administrowanie stronami',
        'icon': '💾',
        'color': '#10b981',
        'category': 'Technik programista',
        'description': 'Tworzenie i administrowanie stronami i aplikacjami internetowymi oraz bazami danych'
    },
    'ee09': {
        'id': 'ee09',
        'name': 'EE.09',
        'title': 'Programowanie aplikacji internetowych',
        'icon': '🌍',
        'color': '#ec4899',
        'category': 'Technik programista (stara podstawa)',
        'description': 'Tworzenie aplikacji internetowych i baz danych oraz administrowanie bazami'
    },
    'e14': {
        'id': 'e14',
        'name': 'E.14',
        'title': 'Tworzenie aplikacji internetowych i baz danych',
        'icon': '📊',
        'color': '#f43f5e',
        'category': 'Technik programista (bardzo stara podstawa)',
        'description': 'Tworzenie aplikacji internetowych, baz danych i administrowanie bazami danych'
    },
    'inf04': {
        'id': 'inf04',
        'name': 'INF.04',
        'title': 'Projektowanie, programowanie i testowanie aplikacji',
        'icon': '📱',
        'color': '#a855f7',
        'category': 'Technik programista',
        'description': 'Projektowanie, programowanie i testowanie aplikacji desktopowych i mobilnych'
    }
}


# Информация о категориях
CATEGORIES_INFO = [
    {"code": "E.12", "name": "E.12", "icon": "🔌"},
    {"code": "E.13", "name": "E.13", "icon": "⚡"},
    {"code": "INF.02", "name": "INF.02 / EE.08", "icon": "🖥️"},
    {"code": "INF.03", "name": "INF.03 / EE.09 / E.14", "icon": "💾"},
    {"code": "INF.04", "name": "INF.04", "icon": "📱"},
]

def get_model_by_code(category_code: str):
    """Получить модель по коду категории"""
    # Приводим к верхнему регистру и убираем лишнее
    code = category_code.upper().replace('-', '.').split('.')[0]
    
    if code == "E12" or code == "E":
        return models.QuestionE12
    elif code == "E13":
        return models.QuestionE13
    elif code == "INF02" or code == "EE08":
        return models.QuestionINF02
    elif code == "INF03" or code == "EE09" or code == "INF03EE09E14":
        return models.QuestionINF03
    elif code == "INF04":
        return models.QuestionINF04
    
    return None

@app.get("/")
def root():
    return {"message": "WEB3Informatyk API", "status": "online"}

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """Получить список всех категорий с количеством вопросов"""
    
    result = []
    total_count = 0
    
    for cat_info in CATEGORIES_INFO:
        model = CATEGORY_MODELS[cat_info["code"]]
        count = db.query(model).count()
        
        result.append({
            "code": cat_info["code"],
            "name": cat_info["name"],
            "icon": cat_info["icon"],
            "question_count": count,
            "test_count": 4  # 40, 20, 1, baza
        })
        
        total_count += count
    
    return {
        "categories": result,
        "total_questions": total_count
    }

@app.get("/api/tests/{category_code}", response_model=schemas.TestResponse)
def get_test(category_code: str, db: Session = Depends(get_db)):
    """Получить тест по категории - ВСЕГДА СЛУЧАЙНЫЕ ВОПРОСЫ"""
    
    # Конфигурация тестов
    test_configs = {
        "e12-40": {"name": "E.12", "title": "Test 40 pytań", "icon": "🔌", "count": 40, "base": "E12"},
        "e12-20": {"name": "E.12", "title": "Test 20 pytań", "icon": "🔌", "count": 20, "base": "E12"},
        "e12-1": {"name": "E.12", "title": "Losowe pytanie", "icon": "🔌", "count": 1, "base": "E12"},
        "e12-baza": {"name": "E.12", "title": "Baza pytań", "icon": "🔌", "count": None, "base": "E12"},
        
        "e13-40": {"name": "E.13", "title": "Test 40 pytań", "icon": "⚡", "count": 40, "base": "E13"},
        "e13-20": {"name": "E.13", "title": "Test 20 pytań", "icon": "⚡", "count": 20, "base": "E13"},
        "e13-1": {"name": "E.13", "title": "Losowe pytanie", "icon": "⚡", "count": 1, "base": "E13"},
        "e13-baza": {"name": "E.13", "title": "Baza pytań", "icon": "⚡", "count": None, "base": "E13"},
        
        "inf02-40": {"name": "INF.02 / EE.08", "title": "Test 40 pytań", "icon": "🖥️", "count": 40, "base": "INF02"},
        "inf02-20": {"name": "INF.02 / EE.08", "title": "Test 20 pytań", "icon": "🖥️", "count": 20, "base": "INF02"},
        "inf02-1": {"name": "INF.02 / EE.08", "title": "Losowe pytanie", "icon": "🖥️", "count": 1, "base": "INF02"},
        "inf02-baza": {"name": "INF.02 / EE.08", "title": "Baza pytań", "icon": "🖥️", "count": None, "base": "INF02"},
        
        "inf03-40": {"name": "INF.03 / EE.09", "title": "Test 40 pytań", "icon": "💾", "count": 40, "base": "INF03"},
        "inf03-20": {"name": "INF.03 / EE.09", "title": "Test 20 pytań", "icon": "💾", "count": 20, "base": "INF03"},
        "inf03-1": {"name": "INF.03 / EE.09", "title": "Losowe pytanie", "icon": "💾", "count": 1, "base": "INF03"},
        "inf03-baza": {"name": "INF.03 / EE.09", "title": "Baza pytań", "icon": "💾", "count": None, "base": "INF03"},
        
        "inf04-40": {"name": "INF.04", "title": "Test 40 pytań", "icon": "📱", "count": 40, "base": "INF04"},
        "inf04-20": {"name": "INF.04", "title": "Test 20 pytań", "icon": "📱", "count": 20, "base": "INF04"},
        "inf04-1": {"name": "INF.04", "title": "Losowe pytanie", "icon": "📱", "count": 1, "base": "INF04"},
        "inf04-baza": {"name": "INF.04", "title": "Baza pytań", "icon": "📱", "count": None, "base": "INF04"},
    }
    
    if category_code not in test_configs:
        raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")
    
    config = test_configs[category_code]
    
    # Получаем модель для категории
    model = get_model_by_code(config["base"])
    if not model:
        raise HTTPException(status_code=404, detail="Model nie znaleziony")
    
    # Получаем ВСЕ вопросы из таблицы
    all_questions = db.query(model).all()
    
    if not all_questions:
        raise HTTPException(status_code=404, detail="Brak pytań dla tej kategorii")
    
    # ВАЖНО: Если count = None (база вопросов), берем ВСЕ вопросы
    if config["count"] is None:
        questions = all_questions
    else:
        # Для тестов - выбираем случайные вопросы
        count = min(config["count"], len(all_questions))
        questions = random.sample(all_questions, count)
        random.shuffle(questions)
    
    # Форматируем для фронтенда
    formatted_questions = []
    for q in questions:
        # Для базы вопросов НЕ перемешиваем ответы
        if config["count"] is None:
            # База вопросов - ответы в оригинальном порядке
            answers = [
                {"id": "a", "text": q.answer_a},
                {"id": "b", "text": q.answer_b},
                {"id": "c", "text": q.answer_c},
                {"id": "d", "text": q.answer_d},
            ]
            correct_answer_new = q.correct_answer
        else:
            # Тесты - перемешиваем ответы
            answers = [
                {"id": "a", "text": q.answer_a, "original": "a"},
                {"id": "b", "text": q.answer_b, "original": "b"},
                {"id": "c", "text": q.answer_c, "original": "c"},
                {"id": "d", "text": q.answer_d, "original": "d"},
            ]
            
            random.shuffle(answers)
            
            # Находим новую букву правильного ответа
            correct_answer_new = None
            for i, ans in enumerate(answers):
                if ans["original"] == q.correct_answer:
                    correct_answer_new = chr(97 + i)
                    break
            
            # Присваиваем новые ID
            for i, ans in enumerate(answers):
                ans["id"] = chr(97 + i)
                del ans["original"]
        
        # ИСПРАВЛЕНО: Формируем полный URL для изображения
        image_url = None
        if q.image_url:
            if q.image_url.startswith('/static'):
                image_url = f"http://localhost:8000{q.image_url}"
            else:
                image_url = q.image_url
        
        formatted_questions.append({
            "id": q.id,
            "question": q.question,
            "image": image_url,  # ← Полный URL
            "answers": answers,
            "correctAnswer": correct_answer_new,
            "explanation": q.explanation or ""
        })
    
    return {
        "name": config["name"],
        "title": config["title"],
        "icon": config["icon"],
        "questions": formatted_questions
    }

@app.post("/api/tests/submit", response_model=schemas.ResultResponse)
def submit_test(submission: schemas.TestSubmit, db: Session = Depends(get_db)):
    """Отправить результаты теста"""
    
    # Определяем категорию из category_code
    base_cat = submission.category_code.split('-')[0].upper()
    
    model = get_model_by_code(base_cat)
    if not model:
        raise HTTPException(status_code=404, detail="Model nie znaleziony")
    
    # Получаем ID вопросов из ответов пользователя
    question_ids = [int(qid) for qid in submission.answers.keys()]
    questions = db.query(model).filter(model.id.in_(question_ids)).all()
    
    correct = 0
    total = len(questions)
    
    # Проверяем ответы
    for q in questions:
        user_answer = submission.answers.get(str(q.id))
        if user_answer == q.correct_answer:
            correct += 1
    
    percentage = round((correct / total * 100), 2) if total > 0 else 0
    passed = percentage >= 50
    
    return {
        "score": correct,
        "total": total,
        "percentage": percentage,
        "passed": passed
    }

@app.get("/api/search")
def search(q: str, db: Session = Depends(get_db)):
    """Глобальный поиск по вопросам, тестам и практикам"""
    
    if not q or len(q.strip()) < 2:
        return {"questions": [], "tests": [], "practices": []}
    
    search_query = q.strip()
    query_text = f"%{search_query}%"
    query_lower = search_query.lower()
    
    # Информация о категориях для вопросов
    category_map = {
        "E.12": {"name": "E.12", "icon": "🔌", "key": "e12", "model": models.QuestionE12},
        "E.13": {"name": "E.13", "icon": "⚡", "key": "e13", "model": models.QuestionE13},
        "INF.02": {"name": "INF.02 / EE.08", "icon": "🖥️", "key": "inf02", "model": models.QuestionINF02},
        "INF.03": {"name": "INF.03 / EE.09", "icon": "💾", "key": "inf03", "model": models.QuestionINF03},
        "INF.04": {"name": "INF.04", "icon": "📱", "key": "inf04", "model": models.QuestionINF04},
    }
    
    # === ПОИСК ПО ВОПРОСАМ ===
    all_questions = []
    
    for cat_code, cat_info in category_map.items():
        model = cat_info["model"]
        
        try:
            questions = db.query(model).filter(
                or_(
                    model.question.ilike(query_text),
                    model.answer_a.ilike(query_text),
                    model.answer_b.ilike(query_text),
                    model.answer_c.ilike(query_text),
                    model.answer_d.ilike(query_text)
                )
            ).limit(5).all()
            
            for question_obj in questions:
                question_text = question_obj.question
                if len(question_text) > 100:
                    question_text = question_text[:100] + "..."
                
                all_questions.append({
                    "id": question_obj.id,
                    "question": question_text,
                    "category": f"{cat_info['key']}-baza",
                    "categoryName": cat_info["name"],
                    "icon": cat_info["icon"]
                })
        except Exception as e:
            print(f"Ошибка поиска в {cat_code}: {e}")
            continue
    
    all_questions = all_questions[:10]
    
    # === ПОИСК ПО ТЕСТАМ ===
    tests = []
    
    for cat_code, cat_info in category_map.items():
        model = cat_info["model"]
        
        if (query_lower in cat_info["name"].lower() or 
            query_lower in cat_info["key"].lower() or
            "test" in query_lower or
            "pytań" in query_lower or
            "baza" in query_lower):
            
            try:
                count = db.query(model).count()
                key = cat_info["key"]
                name = cat_info["name"]
                icon = cat_info["icon"]
                
                tests.extend([
                    {
                        "id": f"{key}-40",
                        "title": f"Test 40 pytań {name}",
                        "category": f"{key}-40",
                        "categoryName": name,
                        "type": "test",
                        "questions": min(40, count),
                        "icon": icon
                    },
                    {
                        "id": f"{key}-20",
                        "title": f"Test 20 pytań {name}",
                        "category": f"{key}-20",
                        "categoryName": name,
                        "type": "test",
                        "questions": min(20, count),
                        "icon": icon
                    },
                    {
                        "id": f"{key}-1",
                        "title": f"Losowe pytanie {name}",
                        "category": f"{key}-1",
                        "categoryName": name,
                        "type": "test",
                        "questions": 1,
                        "icon": icon
                    },
                    {
                        "id": f"{key}-baza",
                        "title": f"Baza pytań {name}",
                        "category": f"{key}-baza",
                        "categoryName": name,
                        "type": "database",
                        "questions": count,
                        "icon": icon
                    }
                ])
            except Exception as e:
                print(f"Ошибка подсчета в {cat_code}: {e}")
                continue
    
    tests = tests[:8]
    
    # === ПОИСК ПО ПРАКТИКАМ ===
    practices = []
    
    for profile_id, profile_info in PRACTICE_PROFILES_INFO.items():
        # Проверяем совпадение с названием профиля, категорией или описанием
        if (query_lower in profile_info['name'].lower() or
            query_lower in profile_info['title'].lower() or
            query_lower in profile_info['category'].lower() or
            query_lower in profile_info['description'].lower() or
            query_lower in profile_id.lower() or
            "praktyka" in query_lower or
            "arkusz" in query_lower):
            
            model = PRACTICE_MODELS.get(profile_id)
            if not model:
                continue
            
            try:
                # Ищем архивы по коду или дате
                archives = db.query(model).filter(
                    or_(
                        model.code.ilike(query_text),
                        model.date.ilike(query_text)
                    )
                ).limit(3).all()
                
                # Если нашли конкретные архивы - добавляем их
                if archives:
                    for archive in archives:
                        practices.append({
                            "id": f"{profile_id}-{archive.id}",
                            "type": "archive",
                            "profile_id": profile_id,
                            "archive_id": archive.id,
                            "title": archive.code,
                            "subtitle": archive.date,
                            "category": profile_info['name'],
                            "icon": profile_info['icon'],
                            "color": profile_info['color']
                        })
                else:
                    # Если не нашли конкретные архивы - добавляем сам профиль
                    archives_count = db.query(model).count()
                    practices.append({
                        "id": profile_id,
                        "type": "profile",
                        "profile_id": profile_id,
                        "title": profile_info['name'],
                        "subtitle": profile_info['title'],
                        "category": profile_info['category'],
                        "icon": profile_info['icon'],
                        "color": profile_info['color'],
                        "archives_count": archives_count
                    })
            
            except Exception as e:
                print(f"Ошибка поиска практик в {profile_id}: {e}")
                continue
    
    practices = practices[:8]
    
    return {
        "questions": all_questions,
        "tests": tests,
        "practices": practices
    }

@app.get("/api/practice/profiles")
def get_practice_profiles(db: Session = Depends(get_db)):
    """Получить список всех профилей практики с количеством архивов"""
    
    result = []
    
    for profile_id, profile_info in PRACTICE_PROFILES_INFO.items():
        model = PRACTICE_MODELS.get(profile_id)
        
        if model:
            # Считаем количество архивов и скачиваний
            archives_count = db.query(model).count()
            total_downloads = db.query(model).count() * 100  # Пример
            
            result.append({
                **profile_info,
                'archives_count': archives_count,
                'total_downloads': total_downloads
            })
    
    return {"profiles": result}

@app.get("/api/practice/profile/{profile_id}")
def get_practice_profile(profile_id: str, db: Session = Depends(get_db)):
    """Получить детали профиля с архивами"""
    
    if profile_id not in PRACTICE_PROFILES_INFO:
        raise HTTPException(status_code=404, detail="Profil nie znaleziony")
    
    profile_info = PRACTICE_PROFILES_INFO[profile_id]
    model = PRACTICE_MODELS.get(profile_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model nie znaleziony")
    
    # Получаем все архивы для этого профиля
    archives = db.query(model).order_by(model.year.desc(), model.date.desc()).all()
    
    # Конвертируем пути файлов в URL
    def file_to_url(file_path):
        if not file_path:
            return None
        # Если путь начинается с downloaded_practice, добавляем /static/
        if file_path.startswith('downloaded_practice'):
            return f"/static/{file_path}"
        # Если уже есть /static/, возвращаем как есть
        if file_path.startswith('/static/'):
            return file_path
        return file_path
    
    # Форматируем архивы
    formatted_archives = []
    for archive in archives:
        # Базовые файлы
        files = {
            'arkusz': file_to_url(archive.arkusz_url),
            'pliki': file_to_url(getattr(archive, 'pliki_url', None)),
        }
        
        # Для INF.04 - специальные поля
        if profile_id == 'inf04':
            files.update({
                'klucz_odpowiedzi': file_to_url(getattr(archive, 'klucz_odpowiedzi_url', None)),
                'materialy': file_to_url(getattr(archive, 'materialy_url', None)),
                'rozwiazanie_cs': file_to_url(getattr(archive, 'rozwiazanie_cs_url', None)),
                'rozwiazanie_cpp': file_to_url(getattr(archive, 'rozwiazanie_cpp_url', None)),
                'rozwiazanie_java': file_to_url(getattr(archive, 'rozwiazanie_java_url', None)),
                'rozwiazanie_python': file_to_url(getattr(archive, 'rozwiazanie_python_url', None)),
            })
        else:
            # Для остальных профилей - обычное rozwiazanie
            files['rozwiazanie'] = file_to_url(getattr(archive, 'rozwiazanie_url', None))
        
        formatted_archives.append({
            'id': archive.id,
            'code': archive.code,
            'date': archive.date,
            'year': archive.year,
            'type': 'Egzamin główny',
            'downloaded': 1000 + archive.id * 100,  # Пример счетчика
            'files': files
        })
    
    return {
        **profile_info,
        'archives': formatted_archives,
        'archives_count': len(formatted_archives),
        'total_downloads': sum(a['downloaded'] for a in formatted_archives)
    }

@app.get("/api/practice/archive/{profile_id}/{archive_id}")
def get_practice_archive(profile_id: str, archive_id: int, db: Session = Depends(get_db)):
    """Получить детали конкретного архива"""
    
    if profile_id not in PRACTICE_MODELS:
        raise HTTPException(status_code=404, detail="Profil nie znaleziony")
    
    model = PRACTICE_MODELS[profile_id]
    archive = db.query(model).filter(model.id == archive_id).first()
    
    if not archive:
        raise HTTPException(status_code=404, detail="Arkusz nie znaleziony")
    
    # Конвертируем пути файлов в URL
    def file_to_url(file_path):
        if not file_path:
            return None
        if file_path.startswith('downloaded_practice'):
            return f"/static/{file_path}"
        if file_path.startswith('/static/'):
            return file_path
        return file_path
    
    # Форматируем файлы
    files = {
        'arkusz': file_to_url(archive.arkusz_url),
        'pliki': file_to_url(archive.pliki_url),
        'rozwiazanie': file_to_url(archive.rozwiazanie_url),
    }
    
    # Для INF.04 добавляем дополнительные поля
    if profile_id == 'inf04':
        files.update({
            'klucz_odpowiedzi': file_to_url(getattr(archive, 'klucz_odpowiedzi_url', None)),
            'materialy': file_to_url(getattr(archive, 'materialy_url', None)),
            'rozwiazanie_cs': file_to_url(getattr(archive, 'rozwiazanie_cs_url', None)),
            'rozwiazanie_cpp': file_to_url(getattr(archive, 'rozwiazanie_cpp_url', None)),
            'rozwiazanie_java': file_to_url(getattr(archive, 'rozwiazanie_java_url', None)),
            'rozwiazanie_python': file_to_url(getattr(archive, 'rozwiazanie_python_url', None)),
        })
    
    return {
        'id': archive.id,
        'code': archive.code,
        'date': archive.date,
        'year': archive.year,
        'type': archive.type,
        'profile': profile_id,
        'profile_info': PRACTICE_PROFILES_INFO[profile_id],
        'files': files,
        'downloaded': 1000 + archive.id * 100
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)