from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_
import random
import os

from .database import get_db, Base, engine
from . import models, schemas

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="WEB3Informatyk API")

# Статические файлы (изображения)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
    """Глобальный поиск по вопросам и тестам"""
    
    if not q or len(q.strip()) < 2:
        return {"questions": [], "tests": []}
    
    search_query = q.strip()  # ← Сохраняем оригинальный запрос
    query_text = f"%{search_query}%"
    
    # Информация о категориях
    category_map = {
        "E.12": {"name": "E.12", "icon": "🔌", "key": "e12", "model": models.QuestionE12},
        "E.13": {"name": "E.13", "icon": "⚡", "key": "e13", "model": models.QuestionE13},
        "INF.02": {"name": "INF.02 / EE.08", "icon": "🖥️", "key": "inf02", "model": models.QuestionINF02},
        "INF.03": {"name": "INF.03 / EE.09", "icon": "💾", "key": "inf03", "model": models.QuestionINF03},
        "INF.04": {"name": "INF.04", "icon": "📱", "key": "inf04", "model": models.QuestionINF04},
    }
    
    all_questions = []
    
    # Ищем в каждой таблице
    for cat_code, cat_info in category_map.items():
        model = cat_info["model"]
        
        try:
            # Поиск по вопросам и ответам
            questions = db.query(model).filter(
                or_(
                    model.question.ilike(query_text),
                    model.answer_a.ilike(query_text),
                    model.answer_b.ilike(query_text),
                    model.answer_c.ilike(query_text),
                    model.answer_d.ilike(query_text)
                )
            ).limit(5).all()
            
            for question_obj in questions:  # ← ИСПРАВЛЕНО: question_obj вместо q
                # Обрезаем длинный текст
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
    
    # Ограничиваем общее количество до 10
    all_questions = all_questions[:10]
    
    # Тесты
    tests = []
    query_lower = search_query.lower()  # ← ИСПРАВЛЕНО: используем search_query
    
    for cat_code, cat_info in category_map.items():
        model = cat_info["model"]
        
        # Проверяем соответствие поисковому запросу
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
    
    # Ограничиваем тесты
    tests = tests[:8]
    
    return {
        "questions": all_questions,
        "tests": tests
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)