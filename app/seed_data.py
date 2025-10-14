from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import Question

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Примерные данные для тестирования
SAMPLE_QUESTIONS = [
    # INF.02 / EE.08
    {
        "category_code": "INF.02",
        "question": "Który protokół jest używany do bezpiecznego przesyłania plików?",
        "image_url": None,
        "answer_a": "FTP",
        "answer_b": "SFTP",
        "answer_c": "HTTP",
        "answer_d": "SMTP",
        "correct_answer": "b",
        "explanation": "SFTP (SSH File Transfer Protocol) zapewnia bezpieczne szyfrowane połączenie do przesyłania plików."
    },
    {
        "category_code": "INF.02",
        "question": "Jaka jest domyślna maska podsieci dla klasy C?",
        "image_url": None,
        "answer_a": "255.0.0.0",
        "answer_b": "255.255.0.0",
        "answer_c": "255.255.255.0",
        "answer_d": "255.255.255.255",
        "correct_answer": "c",
        "explanation": "Klasa C ma domyślną maskę 255.255.255.0, co daje 254 użyteczne adresy host w sieci."
    },
    {
        "category_code": "INF.02",
        "question": "Który port używa protokół HTTPS?",
        "image_url": None,
        "answer_a": "80",
        "answer_b": "443",
        "answer_c": "8080",
        "answer_d": "22",
        "correct_answer": "b",
        "explanation": "HTTPS używa portu 443 do bezpiecznej komunikacji HTTP z szyfrowaniem SSL/TLS."
    },
    # INF.03 / EE.09
    {
        "category_code": "INF.03",
        "question": "Która właściwość CSS służy do zmiany koloru tekstu?",
        "image_url": None,
        "answer_a": "background-color",
        "answer_b": "color",
        "answer_c": "text-color",
        "answer_d": "font-color",
        "correct_answer": "b",
        "explanation": "Właściwość 'color' w CSS służy do ustawiania koloru tekstu elementu."
    },
    {
        "category_code": "INF.03",
        "question": "Która metoda HTTP jest używana do wysyłania danych formularza?",
        "image_url": None,
        "answer_a": "GET",
        "answer_b": "POST",
        "answer_c": "PUT",
        "answer_d": "DELETE",
        "correct_answer": "b",
        "explanation": "POST jest standardową metodą do wysyłania danych formularza."
    },
    # INF.04
    {
        "category_code": "INF.04",
        "question": "Która funkcja w JavaScript służy do wyświetlania komunikatu w konsoli?",
        "image_url": None,
        "answer_a": "alert()",
        "answer_b": "console.log()",
        "answer_c": "print()",
        "answer_d": "display()",
        "correct_answer": "b",
        "explanation": "console.log() wyświetla informacje w konsoli przeglądarki."
    },
    {
        "category_code": "INF.04",
        "question": "Co to jest JSON?",
        "image_url": None,
        "answer_a": "JavaScript Object Notation",
        "answer_b": "Java Standard Object Notation",
        "answer_c": "JavaScript Ordered Network",
        "answer_d": "Java Source Object Node",
        "correct_answer": "a",
        "explanation": "JSON to lekki format wymiany danych."
    },
    # E.12
    {
        "category_code": "E.12",
        "question": "Która magistrala jest używana do podłączania dysków SSD?",
        "image_url": None,
        "answer_a": "PCI",
        "answer_b": "AGP",
        "answer_c": "SATA",
        "answer_d": "ISA",
        "correct_answer": "c",
        "explanation": "SATA to standard interfejsu do podłączania dysków."
    },
    {
        "category_code": "E.12",
        "question": "Ile pinów ma złącze procesora Intel LGA 1200?",
        "image_url": None,
        "answer_a": "1150",
        "answer_b": "1151",
        "answer_c": "1200",
        "answer_d": "1700",
        "correct_answer": "c",
        "explanation": "LGA 1200 to gniazdo z 1200 pinami."
    },
    # E.13
    {
        "category_code": "E.13",
        "question": "Jaki jest zakres adresów IP klasy A?",
        "image_url": None,
        "answer_a": "1.0.0.0 - 126.255.255.255",
        "answer_b": "128.0.0.0 - 191.255.255.255",
        "answer_c": "192.0.0.0 - 223.255.255.255",
        "answer_d": "224.0.0.0 - 239.255.255.255",
        "correct_answer": "a",
        "explanation": "Klasa A obejmuje adresy od 1.0.0.0 do 126.255.255.255."
    },
]

def seed_database():
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже данные
        existing = db.query(Question).first()
        if existing:
            print("База данных уже содержит данные. Пропускаем загрузку.")
            return
        
        # Добавляем данные
        for q_data in SAMPLE_QUESTIONS:
            question = Question(**q_data)
            db.add(question)
        
        db.commit()
        print(f"Успешно добавлено {len(SAMPLE_QUESTIONS)} вопросов в базу данных!")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()