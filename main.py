from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import random
import sqlite3
from database import init_db, save_result

app = FastAPI(title="Ai Adaptiv Edu")
init_db() # Dastur yonganda bazani (va yangi savollarni) tayyorlaydi

# Static fayllar (CSS/JS uchun)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- FOYDALANUVCHI QISMI (Frontend) ---

@app.get("/", response_class=HTMLResponse)
def home():
    """Asosiy sahifani yuklaydi"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

# 1. ADAPTIV SAVOL OLISH FUNKSIYASI
def get_question_from_db(difficulty):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    # Berilgan qiyinlikdagi savollarni olish
    cursor.execute('SELECT id, subject, question_text, options, correct_answer FROM questions WHERE difficulty = ?', (difficulty,))
    questions = cursor.fetchall()
    conn.close()
    
    if questions:
        q = random.choice(questions)
        return {
            "id": q[0],
            "subject": q[1],
            "question": q[2],
            "options": q[3].split(", "), # Variantlarni listga aylantirish
            "correct": q[4]
        }
    return None

@app.get("/start")
def start_test(name: str):
    # Test boshlanganda 1-darajali (oson) savol beriladi
    first_q = get_question_from_db(1)
    return {
        "student": name, 
        "question": first_q, 
        "current_difficulty": 1,
        "step": 1,
        "score": 0
    }

# 2. MUKAMMAL ADAPTIV TEKSHIRISH ALGORITMI
@app.post("/check")
async def check_adaptive_answer(request: Request):
    data = await request.json()
    name = data["name"]
    question_id = data["question_id"]
    user_answer = data["answer"]
    current_diff = data["current_difficulty"]
    score = data["score"]
    step = data["step"]

    # Bazadan to'g'ri javobni tekshirish
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT correct_answer FROM questions WHERE id = ?', (question_id,))
    res = cursor.fetchone()
    correct_answer = res[0] if res else ""
    conn.close()

    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

    # ADAPTIV MANTIQ:
    if is_correct:
        score += 1
        # To'g'ri bo'lsa darajani oshirish (max 3)
        next_diff = min(current_diff + 1, 3)
        feedback = "To'g'ri! Daraja oshirildi."
    else:
        # Xato bo'lsa darajani tushirish (min 1)
        next_diff = max(current_diff - 1, 1)
        feedback = f"Xato! To'g'ri javob: {correct_answer}. Daraja tushirildi."

    # Testni 10 ta savoldan keyin tugatish
    if step >= 10:
        percent = (score / 10) * 100
        summary = "A'lo! Siz barcha qiyinlik darajalarini bosib o'tdingiz." if percent > 80 else "Yaxshi, lekin ko'proq ishlash kerak."
        save_result(name, percent, summary)
        return {"finished": True, "percent": percent, "summary": summary}

    # Keyingi adaptiv savolni olish
    next_q = get_question_from_db(next_diff)

    return {
        "finished": False,
        "question": next_q,
        "next_difficulty": next_diff,
        "score": score,
        "step": step + 1,
        "feedback": feedback
    }

# --- ADMIN PANEL QISMI ---

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    """Admin panelning asosiy sahifasini yuklaydi"""
    try:
        with open("templates/admin.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Xatolik: templates/admin.html fayli topilmadi!"

@app.get("/api/results")
def get_results_api():
    """Bazadagi natijalarni JSON formatida admin panelga yuboradi"""
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    # Natijalarni vaqti bo'yicha saralab olish
    cursor.execute('SELECT student_name, total_percent, summary, timestamp FROM results ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "name": row[0],
            "percent": row[1],
            "feedback": row[2],
            "date": row[3]
        })
    return results

@app.get("/get_results")
def get_results():
    """Eski formatdagi natijalarni olish (ixtiyoriy)"""
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT student_name, total_percent, summary FROM results ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows