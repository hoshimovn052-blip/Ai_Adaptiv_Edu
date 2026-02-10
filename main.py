from fastapi import FastAPI, Request, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import sqlite3
import time
from database import init_db, save_result

app = FastAPI(title="Ai Adaptiv Edu - Pro")
init_db()

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

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- YORDAMCHI FUNKSIYALAR ---

def get_db_connection():
    conn = sqlite3.connect('edu_platform.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- FANLAR RO'YXATI (Siz so'ragan qism) ---
@app.get("/api/subjects")
def get_subjects():
    return ["Matematika", "Fizika", "Informatika", "Biologiya", "Geografiya", "Ingliz tili", "Kimyo"]

# Fanga oid video va yangiliklarni olish
@app.get("/api/content/{subject}")
def get_content(subject: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT content_type, title, data FROM content WHERE subject = ?', (subject,))
    rows = cursor.fetchall()
    conn.close()
    return [{"type": r[0], "title": r[1], "data": r[2]} for r in rows]

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

# --- YO'NALISHLAR ---

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Xatolik: templates/index.html topilmadi!"

@app.get("/start")
async def start_test(name: str, subject: str = "Umumiy"):
    first_q = get_question(1, subject)
    if not first_q:
        return {"error": f"{subject} fani bo'yicha savollar topilmadi!"}
        
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

    correct_answer = row["correct_answer"]
    is_correct = user_ans.strip().lower() == correct_answer.strip().lower()
    
    new_score = score + 1 if is_correct else score
    next_diff = min(curr_diff + 1, 3) if is_correct else max(curr_diff - 1, 1)

    if step >= 10:
        end_time = time.time()
        spent_time = round((end_time - start_time) / 60, 1)
        percent = (new_score / 10) * 100
        
        if percent >= 90:
            summary = f"A'lo! {spent_time} daqiqada {subject}ni {percent}% ga yopdingiz. Darajangiz: Ekspert."
        elif percent >= 70:
            summary = f"Yaxshi! {spent_time} daqiqada {percent}%. Bilimingiz barqaror."
        else:
            summary = f"Diqqat! Natija {percent}%. Mavzularni qayta o'qish tavsiya etiladi."

        background_tasks.add_task(save_result, name, percent, summary, subject)
        return {"finished": True, "percent": percent, "summary": summary, "time": spent_time}

    next_q = get_question(next_diff, subject)
    return {
        "finished": False, "question": next_q, "next_difficulty": next_diff,
        "score": new_score, "step": step + 1, "is_correct": is_correct
    }

# --- ADMIN PANEL ---

@app.get("/admin", response_class=HTMLResponse)
def admin_page(username: str = Depends(authenticate_teacher)):
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Xatolik: templates/admin.html topilmadi!"

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