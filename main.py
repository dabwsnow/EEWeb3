from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv 
import os 
import random
import json
from pathlib import Path

from database import get_db, Base, engine
import models, schemas

load_dotenv()

Base.metadata.create_all(bind=engine)

CONFIG = {}
config_path = Path("config.json")
if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    print("⚠️ Warning: config.json not found, using empty config")
    CONFIG = {
        "categories_info": [],
        "test_configs": {},
        "practice_profiles_info": {}
    }

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app = FastAPI(title="WEB3Informatyk API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

FRONTEND_URLS = os.getenv("FRONTEND_URL").split(",")

FRONTEND_URLS = [url.strip() for url in FRONTEND_URLS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def get_model_by_code(category_code: str):
    code = category_code.upper().replace('-', '.').split('.')[0]
    
    model_map = {
        "E12": models.QuestionE12,
        "E": models.QuestionE12,
        "E13": models.QuestionE13,
        "INF02": models.QuestionINF02,
        "EE08": models.QuestionINF02,
        "INF03": models.QuestionINF03,
        "EE09": models.QuestionINF03,
        "INF03EE09E14": models.QuestionINF03,
        "INF04": models.QuestionINF04,
    }
    
    return model_map.get(code)


def shuffle_answers(question, shuffle: bool = True):
    answers = [
        {"id": "a", "text": question.answer_a, "original": "a"},
        {"id": "b", "text": question.answer_b, "original": "b"},
        {"id": "c", "text": question.answer_c, "original": "c"},
        {"id": "d", "text": question.answer_d, "original": "d"},
    ]
    
    if shuffle:
        random.shuffle(answers)
        
        correct_answer = None
        for i, ans in enumerate(answers):
            if ans["original"] == question.correct_answer:
                correct_answer = chr(97 + i)
                break
        
        for i, ans in enumerate(answers):
            ans["id"] = chr(97 + i)
            del ans["original"]
    else:
        correct_answer = question.correct_answer
        for ans in answers:
            del ans["original"]
    
    return answers, correct_answer


def format_question(question, shuffle_mode: bool = True):
    answers, correct_answer = shuffle_answers(question, shuffle=shuffle_mode)
    
    return {
        "id": question.id,
        "question": question.question,
        "image": question.image_url,
        "answers": answers,
        "correctAnswer": correct_answer,
        "explanation": question.explanation or ""
    }


@app.get("/")
def root():
    return {
        "message": "WEB3Informatyk API",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/api/categories")
@limiter.limit("30/minute")
def get_categories(request: Request, db: Session = Depends(get_db)):
    try:
        result = []
        total_count = 0
        
        for cat_info in CONFIG["categories_info"]:
            model = CATEGORY_MODELS[cat_info["code"]]
            count = db.query(model).count()
            
            result.append({
                "code": cat_info["code"],
                "name": cat_info["name"],
                "icon": cat_info["icon"],
                "question_count": count,
                "test_count": 4
            })
            
            total_count += count
        
        return {
            "categories": result,
            "total_questions": total_count
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/tests/{category_code}", response_model=schemas.TestResponse)
@limiter.limit("20/minute")
def get_test(request: Request, category_code: str, db: Session = Depends(get_db)):
    try:
        test_configs = CONFIG["test_configs"]
        
        if category_code not in test_configs:
            raise HTTPException(status_code=404, detail="Kategoria nie znaleziona")
        
        config = test_configs[category_code]
        model = get_model_by_code(config["base"])
        
        if not model:
            raise HTTPException(status_code=404, detail="Model nie znaleziony")
        
        all_questions = db.query(model).all()
        
        if not all_questions:
            raise HTTPException(status_code=404, detail="Brak pytań dla tej kategorii")
        
        if config["count"] is None:
            questions = all_questions
            shuffle_mode = False
        else:
            count = min(config["count"], len(all_questions))
            questions = random.sample(all_questions, count)
            random.shuffle(questions)
            shuffle_mode = True
        
        formatted_questions = [
            format_question(q, shuffle_mode=shuffle_mode) 
            for q in questions
        ]
        
        return {
            "name": config["name"],
            "title": config["title"],
            "icon": config["icon"],
            "questions": formatted_questions
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/tests/submit", response_model=schemas.ResultResponse)
@limiter.limit("30/minute")
def submit_test(request: Request, submission: schemas.TestSubmit, db: Session = Depends(get_db)):
    try:
        base_cat = submission.category_code.split('-')[0].upper()
        model = get_model_by_code(base_cat)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model nie znaleziony")
        
        question_ids = [int(qid) for qid in submission.answers.keys()]
        
        if len(question_ids) > 100:
            raise HTTPException(status_code=400, detail="Too many questions")
        
        questions = db.query(model).filter(model.id.in_(question_ids)).all()
        
        correct = sum(
            1 for q in questions 
            if submission.answers.get(str(q.id)) == q.correct_answer
        )
        
        total = len(questions)
        percentage = round((correct / total * 100), 2) if total > 0 else 0
        passed = percentage >= 50
        
        return {
            "score": correct,
            "total": total,
            "percentage": percentage,
            "passed": passed
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/search")
@limiter.limit("20/minute")
def search(request: Request, q: str, db: Session = Depends(get_db)):
    try:
        if not q or len(q.strip()) < 2:
            return {"questions": [], "tests": [], "practices": []}
        
        if len(q.strip()) > 200:
            raise HTTPException(status_code=400, detail="Query too long")
        
        search_query = q.strip()
        query_text = f"%{search_query}%"
        query_lower = search_query.lower()
        
        category_map = {
            "E.12": {"name": "E.12", "icon": "🔌", "key": "e12", "model": models.QuestionE12},
            "E.13": {"name": "E.13", "icon": "⚡", "key": "e13", "model": models.QuestionE13},
            "INF.02": {"name": "INF.02 / EE.08", "icon": "🖥️", "key": "inf02", "model": models.QuestionINF02},
            "INF.03": {"name": "INF.03 / EE.09", "icon": "💾", "key": "inf03", "model": models.QuestionINF03},
            "INF.04": {"name": "INF.04", "icon": "📱", "key": "inf04", "model": models.QuestionINF04},
        }
        
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
            except Exception:
                continue
        
        all_questions = all_questions[:10]
        
        tests = []
        test_keywords = ["test", "pytań", "baza", "losowe"]
        
        for cat_code, cat_info in category_map.items():
            should_include = (
                query_lower in cat_info["name"].lower() or 
                query_lower in cat_info["key"].lower() or
                any(keyword in query_lower for keyword in test_keywords)
            )
            
            if should_include:
                try:
                    count = db.query(cat_info["model"]).count()
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
                except Exception:
                    continue
        
        tests = tests[:8]
        
        practices = []
        practice_keywords = ["praktyka", "arkusz", "egzamin"]
        
        for profile_id, profile_info in CONFIG["practice_profiles_info"].items():
            model = PRACTICE_MODELS.get(profile_id)
            if not model:
                continue
            
            try:
                archives = db.query(model).filter(
                    or_(
                        model.code.ilike(query_text),
                        model.date.ilike(query_text)
                    )
                ).limit(5).all()
                
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
            except Exception:
                continue
        
        for profile_id, profile_info in CONFIG["practice_profiles_info"].items():
            should_include = (
                query_lower in profile_info['name'].lower() or
                query_lower in profile_info['title'].lower() or
                query_lower in profile_info['category'].lower() or
                query_lower in profile_info['description'].lower() or
                query_lower in profile_id.lower() or
                any(keyword in query_lower for keyword in practice_keywords)
            )
            
            if should_include:
                model = PRACTICE_MODELS.get(profile_id)
                if not model:
                    continue
                
                try:
                    already_added = any(p.get('profile_id') == profile_id for p in practices)
                    
                    if not already_added:
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
                except Exception:
                    continue
        
        practices = practices[:10]
        
        return {
            "questions": all_questions,
            "tests": tests,
            "practices": practices
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/practice/profiles")
@limiter.limit("30/minute")
def get_practice_profiles(request: Request, db: Session = Depends(get_db)):
    try:
        result = []
        
        for profile_id, profile_info in CONFIG["practice_profiles_info"].items():
            model = PRACTICE_MODELS.get(profile_id)
            
            if model:
                archives_count = db.query(model).count()
                total_downloads = archives_count * 100
                
                result.append({
                    **profile_info,
                    'archives_count': archives_count,
                    'total_downloads': total_downloads
                })
        
        return {"profiles": result}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/practice/profile/{profile_id}")
@limiter.limit("30/minute")
def get_practice_profile(request: Request, profile_id: str, db: Session = Depends(get_db)):
    try:
        if profile_id not in CONFIG["practice_profiles_info"]:
            raise HTTPException(status_code=404, detail="Profil nie znaleziony")
        
        profile_info = CONFIG["practice_profiles_info"][profile_id]
        model = PRACTICE_MODELS.get(profile_id)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model nie znaleziony")
        
        archives = db.query(model).order_by(
            model.year.desc(), 
            model.date.desc()
        ).all()
        
        formatted_archives = []
        for archive in archives:
            files = {
                'arkusz': archive.arkusz_url,
                'pliki': getattr(archive, 'pliki_url', None),
            }
            
            if profile_id == 'inf04':
                files.update({
                    'klucz_odpowiedzi': getattr(archive, 'klucz_odpowiedzi_url', None),
                    'materialy': getattr(archive, 'materialy_url', None),
                    'rozwiazanie_cs': getattr(archive, 'rozwiazanie_cs_url', None),
                    'rozwiazanie_cpp': getattr(archive, 'rozwiazanie_cpp_url', None),
                    'rozwiazanie_java': getattr(archive, 'rozwiazanie_java_url', None),
                    'rozwiazanie_python': getattr(archive, 'rozwiazanie_python_url', None),
                })
            else:
                files['rozwiazanie'] = getattr(archive, 'rozwiazanie_url', None)
            
            formatted_archives.append({
                'id': archive.id,
                'code': archive.code,
                'date': archive.date,
                'year': archive.year,
                'type': 'Egzamin główny',
                'downloaded': 1000 + archive.id * 100,
                'files': files
            })
        
        return {
            **profile_info,
            'archives': formatted_archives,
            'archives_count': len(formatted_archives),
            'total_downloads': sum(a['downloaded'] for a in formatted_archives)
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/practice/archive/{profile_id}/{archive_id}")
@limiter.limit("30/minute")
def get_practice_archive(request: Request, profile_id: str, archive_id: int, db: Session = Depends(get_db)):
    try:
        if profile_id not in PRACTICE_MODELS:
            raise HTTPException(status_code=404, detail="Profil nie znaleziony")
        
        model = PRACTICE_MODELS[profile_id]
        archive = db.query(model).filter(model.id == archive_id).first()
        
        if not archive:
            raise HTTPException(status_code=404, detail="Arkusz nie znaleziony")
        
        files = {
            'arkusz': archive.arkusz_url,
            'pliki': archive.pliki_url,
            'rozwiazanie': archive.rozwiazanie_url,
        }
        
        if profile_id == 'inf04':
            files.update({
                'klucz_odpowiedzi': getattr(archive, 'klucz_odpowiedzi_url', None),
                'materialy': getattr(archive, 'materialy_url', None),
                'rozwiazanie_cs': getattr(archive, 'rozwiazanie_cs_url', None),
                'rozwiazanie_cpp': getattr(archive, 'rozwiazanie_cpp_url', None),
                'rozwiazanie_java': getattr(archive, 'rozwiazanie_java_url', None),
                'rozwiazanie_python': getattr(archive, 'rozwiazanie_python_url', None),
            })
        
        return {
            'id': archive.id,
            'code': archive.code,
            'date': archive.date,
            'year': archive.year,
            'type': archive.type,
            'profile': profile_id,
            'profile_info': CONFIG["practice_profiles_info"][profile_id],
            'files': files,
            'downloaded': 1000 + archive.id * 100
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
