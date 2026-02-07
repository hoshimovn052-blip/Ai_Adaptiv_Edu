from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import sqlite3
from database import init_db, save_result

app = FastAPI(title="Ai Adaptiv Edu")
init_db() # Dastur yonganda bazani tayyorlaydi

# Xavfsizlik obyekti
security = HTTPBasic()

# O'QTUVCHI LOGIN VA PAROLI
ADMIN_USERNAME = "teacher"
ADMIN_PASSWORD = "admin777"

# Loginni tekshirish funksiyasi
def authenticate_teacher(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol noto'g'ri!",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Static fayllar (CSS/JS uchun)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- FOYDALANUVCHI QISMI (Frontend) ---

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

def get_question_from_db(difficulty):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, subject, question_text, options, correct_answer FROM questions WHERE difficulty = ?', (difficulty,))
    questions = cursor.fetchall()
    conn.close()
    
    if questions:
        q = random.choice(questions)
        return {
            "id": q[0],
            "subject": q[1],
            "question": q[2],
            "options": q[3].split(", "),
            "correct": q[4]
        }
    return None

@app.get("/start")
def start_test(name: str):
    first_q = get_question_from_db(1)
    return {
        "student": name, 
        "question": first_q, 
        "current_difficulty": 1,
        "step": 1,
        "score": 0
    }

@app.post("/check")
async def check_adaptive_answer(request: Request):
    data = await request.json()
    name = data["name"]
    question_id = data["question_id"]
    user_answer = data["answer"]
    current_diff = data["current_difficulty"]
    score = data["score"]
    step = data["step"]

    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT correct_answer FROM questions WHERE id = ?', (question_id,))
    res = cursor.fetchone()
    correct_answer = res[0] if res else ""
    conn.close()

    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

    if is_correct:
        score += 1
        next_diff = min(current_diff + 1, 3)
        feedback_text = "To'g'ri!"
    else:
        next_diff = max(current_diff - 1, 1)
        feedback_text = f"Xato! Javob: {correct_answer}"

    # Test yakunlanishi
    if step >= 10:
        percent = (score / 10) * 100
        # AI Xulosasini aniqlash
        if percent >= 90: summary = "A'lo! Mavzuni mukammal o'zlashtirgansiz."
        elif percent >= 70: summary = "Yaxshi. Bilimlaringizni mustahkamlang."
        elif percent >= 50: summary = "Qoniqarli. Ko'proq mehnat qilish kerak."
        else: summary = "Past natija. Mavzuni boshidan o'qing."
        
        save_result(name, percent, summary)
        return {"finished": True, "percent": percent, "summary": summary}

    next_q = get_question_from_db(next_diff)
    return {
        "finished": False,
        "question": next_q,
        "next_difficulty": next_diff,
        "score": score,
        "step": step + 1,
        "feedback": feedback_text
    }

# --- ADMIN PANEL QISMI (HIMOYA QILINGAN) ---

@app.get("/admin", response_class=HTMLResponse)
def admin_page(username: str = Depends(authenticate_teacher)):
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Xatolik: templates/admin.html topilmadi!"

@app.get("/api/results")
def get_results_api(username: str = Depends(authenticate_teacher)):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    # Bazadagi student_name, total_percent, summary (xulosa), timestamp ni olamiz
    cursor.execute('SELECT student_name, total_percent, summary, timestamp FROM results ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "name": row[0],
            "percent": row[1],
            "feedback": row[2], # Bu yerda row[2] - bu bazadagi 'summary' ustuni
            "date": row[3]
        })
    return results