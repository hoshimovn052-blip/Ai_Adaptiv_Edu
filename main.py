from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import sqlite3
from database import init_db, save_result

app = FastAPI(title="Ai Adaptiv Edu - Multi-Subject Platform")
init_db()

# Xavfsizlik
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

# --- FOYDALANUVCHI API VA YO'NALISHLARI ---

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Fanlar ro'yxati
@app.get("/api/subjects")
def get_subjects():
    return ["Matematika", "Fizika", "Informatika", "Biologiya", "Geografiya", "Ingliz tili", "Kimyo"]

# Fanga oid video va yangiliklarni olish
@app.get("/api/content/{subject}")
def get_content(subject: str):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT content_type, title, data FROM content WHERE subject = ?', (subject,))
    rows = cursor.fetchall()
    conn.close()
    return [{"type": r[0], "title": r[1], "data": r[2]} for r in rows]

# Adaptiv savol olish (Fan bo'yicha yoki Umumiy)
def get_question(difficulty, subject=None):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    if subject and subject != "Umumiy":
        cursor.execute('SELECT id, subject, question_text, options, correct_answer FROM questions WHERE difficulty = ? AND subject = ?', (difficulty, subject))
    else:
        cursor.execute('SELECT id, subject, question_text, options, correct_answer FROM questions WHERE difficulty = ?', (difficulty,))
    
    questions = cursor.fetchall()
    conn.close()
    
    if questions:
        q = random.choice(questions)
        return {"id": q[0], "subject": q[1], "question": q[2], "options": q[3].split(", "), "correct": q[4]}
    return None

@app.get("/start")
def start_test(name: str, subject: str = "Umumiy"):
    first_q = get_question(1, subject)
    return {
        "student": name,
        "subject": subject,
        "question": first_q,
        "current_difficulty": 1,
        "step": 1,
        "score": 0
    }

@app.post("/check")
async def check_answer(request: Request):
    data = await request.json()
    name, q_id, user_ans = data["name"], data["question_id"], data["answer"]
    curr_diff, score, step, subject = data["current_difficulty"], data["score"], data["step"], data.get("subject", "Umumiy")

    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT correct_answer FROM questions WHERE id = ?', (q_id,))
    correct_answer = cursor.fetchone()[0]
    conn.close()

    is_correct = user_ans.strip().lower() == correct_answer.strip().lower()
    
    # Adaptiv mantiq
    if is_correct:
        score += 1
        next_diff = min(curr_diff + 1, 3)
    else:
        next_diff = max(curr_diff - 1, 1)

    if step >= 10:
        percent = (score / 10) * 100
        # AI Tahlil mantiqi
        if percent >= 90: summary = f"Mukammal! {subject} fanini chuqur o'zlashtirgansiz."
        elif percent >= 70: summary = f"Yaxshi natija. {subject} bo'yicha bilimlaringiz mustahkam."
        else: summary = f"Diqqat! {subject} fani ustida ko'proq ishlashingiz kerak."
        
        save_result(name, percent, summary, subject)
        return {"finished": True, "percent": percent, "summary": summary}

    next_q = get_question(next_diff, subject)
    return {
        "finished": False,
        "question": next_q,
        "next_difficulty": next_diff,
        "score": score,
        "step": step + 1,
        "is_correct": is_correct
    }

# --- ADMIN PANEL (SIFATLI VA TAHLILIY) ---

@app.get("/admin", response_class=HTMLResponse)
def admin_page(username: str = Depends(authenticate_teacher)):
    with open("templates/admin.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/results")
def get_results_api(username: str = Depends(authenticate_teacher)):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    # Endi 'subject' ustunini ham olamiz
    cursor.execute('SELECT student_name, total_percent, summary, subject, timestamp FROM results ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        "name": r[0],
        "percent": r[1],
        "feedback": r[2],
        "subject": r[3],
        "date": r[4]
    } for r in rows]