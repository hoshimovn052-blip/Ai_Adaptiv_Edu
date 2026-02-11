from fastapi import FastAPI, Request, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import random
import sqlite3
import time
import os
from database import init_db, save_result

# Bazani BMI talablariga muvofiq ishga tushirish
app = FastAPI(title="Ai Adaptiv Edu - BMI Professional")
init_db()

# --- XAVFSIZLIK (Admin Login) ---
security = HTTPBasic()
ADMIN_USERNAME = "teacher"
ADMIN_PASSWORD = "admin777"

def authenticate_teacher(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kirish taqiqlandi!",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Static fayllar (CSS, JS, Images)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- YORDAMCHI FUNKSIYALAR ---

def get_db_connection():
    conn = sqlite3.connect('edu_platform.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- API: FANLAR VA KONTENTLAR ---

@app.get("/api/subjects")
def get_subjects():
    # BMI uchun barcha asosiy fanlar
    return ["Matematika", "Fizika", "Informatika", "Biologiya", "Geografiya", "Ingliz tili", "Kimyo"]

@app.get("/api/get_content/{subject}/{c_type}")
def get_filtered_content(subject: str, c_type: str):
    """Faqat tanlangan fan va kontent turiga (reels yoki lesson) mos videolarni qaytaradi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT title, data FROM content WHERE subject = ? AND content_type = ?', (subject, c_type))
    rows = cursor.fetchall()
    conn.close()
    return [{"title": r["title"], "url": r["data"]} for r in rows]

# --- ADAPTIV TEST MANTIQI ---

def get_question(difficulty, subject=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if subject and subject != "Umumiy":
        cursor.execute('SELECT * FROM questions WHERE difficulty = ? AND subject = ?', (difficulty, subject))
    else:
        cursor.execute('SELECT * FROM questions WHERE difficulty = ?', (difficulty,))
    
    questions = cursor.fetchall()
    conn.close()
    
    if questions:
        q = random.choice(questions)
        diff_names = {1: "Oson", 2: "O'rta", 3: "Qiyin"}
        return {
            "id": q["id"],
            "subject": q["subject"],
            "question": q["question_text"],
            "options": q["options"].split(", "),
            "difficulty_num": q["difficulty"],
            "difficulty_name": diff_names.get(q["difficulty"], "Noma'lum")
        }
    return None

# --- YO'NALISHLAR (ROUTING) ---

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Xatolik: templates/index.html topilmadi!"

@app.get("/start")
async def start_test(name: str, subject: str = "Umumiy"):
    # Individuallashtirilgan ta'limni diagnostika bilan boshlash (Oson darajadan)
    first_q = get_question(1, subject)
    if not first_q:
        return {"error": f"{subject} fani bo'yicha savollar hali kiritilmagan!"}
        
    return {
        "student": name,
        "subject": subject,
        "question": first_q,
        "current_difficulty": 1,
        "step": 1,
        "score": 0,
        "start_time": time.time()
    }

@app.post("/check")
async def check_answer(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    name = data.get("name")
    q_id = data.get("question_id")
    user_ans = data.get("answer")
    curr_diff = data.get("current_difficulty")
    score = data.get("score")
    step = data.get("step")
    subject = data.get("subject", "Umumiy")
    start_time = data.get("start_time", time.time())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT correct_answer FROM questions WHERE id = ?', (q_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "Savol topilmadi"}

    is_correct = user_ans.strip().lower() == row["correct_answer"].strip().lower()
    
    new_score = score + 1 if is_correct else score
    # Adaptivlik: To'g'ri bo'lsa daraja ko'tariladi, xato bo'lsa tushadi
    next_diff = min(curr_diff + 1, 3) if is_correct else max(curr_diff - 1, 1)

    if step >= 10:
        end_time = time.time()
        spent_time = round((end_time - start_time) / 60, 1)
        percent = (new_score / 10) * 100
        
        # BMI: Individuallashtirilgan AI xulosasi
        if percent >= 90:
            summary = f"A'lo! {spent_time} daqiqada {subject}ni {percent}% ga yopdingiz. Darajangiz: Ekspert."
        elif percent >= 70:
            summary = f"Yaxshi! {spent_time} daqiqada {percent}%. Bilimingiz barqaror, relislarni ko'rishni davom ettiring."
        else:
            summary = f"Diqqat! Natija {percent}%. Sizga {subject} bo'yicha video darslarni qayta ko'rish tavsiya etiladi."

        background_tasks.add_task(save_result, name, percent, summary, subject)
        return {"finished": True, "percent": percent, "summary": summary, "time": spent_time}

    next_q = get_question(next_diff, subject)
    return {
        "finished": False, "question": next_q, "next_difficulty": next_diff,
        "score": new_score, "step": step + 1, "is_correct": is_correct
    }

# --- ADMIN API: KONTENT BOSHQARUVI ---

@app.get("/admin", response_class=HTMLResponse)
def admin_page(username: str = Depends(authenticate_teacher)):
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Xatolik: templates/admin.html topilmadi!"

@app.post("/api/add_content")
async def add_content(request: Request, username: str = Depends(authenticate_teacher)):
    data = await request.json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO content (subject, content_type, title, data) 
            VALUES (?, ?, ?, ?)
        ''', (data['subject'], data['type'], data['title'], data['url']))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@app.get("/api/results")
def get_results_api(username: str = Depends(authenticate_teacher)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT student_name, total_percent, summary, subject, timestamp FROM results ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "name": r["student_name"],
        "percent": r["total_percent"],
        "feedback": r["summary"],
        "subject": r["subject"],
        "date": r["timestamp"]
    } for r in rows]