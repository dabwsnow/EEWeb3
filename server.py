from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
from markupsafe import escape
from jinja2 import Environment, FileSystemLoader

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "images")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "templates")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")

app.mount("/images", StaticFiles(directory=IMAGE_FOLDER), name="images")
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")

env = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER), autoescape=True)

def get_all_questions():
    conn = sqlite3.connect(os.path.join(BASE_DIR, "pytania.db"))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT question, answer_a, answer_b, answer_c, answer_d, correct_index, image_path FROM questions"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    questions = get_all_questions()
    template = env.get_template("index.html")
    return HTMLResponse(template.render(questions=questions))

@app.get("/api/get_answer")
async def get_answer(q: str):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "pytania.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE question LIKE ?", (f"%{q}%",))
    row = cursor.fetchone()
    conn.close()

    if row:
        return JSONResponse({
            "question": escape(row[1]),
            "answers": [escape(row[2]), escape(row[3]), escape(row[4]), escape(row[5])],
            "correct_index": row[6],
            "image": row[7]
        })
    else:
        return JSONResponse({"error": "Nie znaleziono pytania"}, status_code=404)
