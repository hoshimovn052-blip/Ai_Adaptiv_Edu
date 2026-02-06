from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import random
import sqlite3
from database import init_db, save_result

app = FastAPI(title="Ai Adaptiv Edu")
init_db() # Dastur yonganda bazani tayyorlaydi

# 10 ta fan bazasi [cite: 23-29, 130-145]
tests = {
    "Matematika": [{"q": "15 * 4 = ?", "a": "60"}, {"q": "√81 = ?", "a": "9"}],
    "Informatika": [{"q": "Python nima?", "a": "Dasturlash tili"}, {"q": "CPU nima?", "a": "Protsessor"}],
    "Fizika": [{"q": "Kuch birligi?", "a": "Nyuton"}, {"q": "Vaqt birligi?", "a": "Sekund"}],
    "Ingliz tili": [{"q": "Apple nima?", "a": "Olma"}, {"q": "Go' (o'tgan zamoni)?", "a": "Went"}],
    "Kimyo": [{"q": "Suv formulasi?", "a": "H2O"}, {"q": "Oksigen belgisi?", "a": "O"}],
    "Biologiya": [{"q": "DNK nima?", "a": "Genetik ma'lumot"}],
    "Tarix": [{"q": "Amir Temur tug'ilgan yili?", "a": "1336"}],
    "Geografiya": [{"q": "Okean nima?", "a": "Suv havzasi"}],
    "Adabiyot": [{"q": "Navoiy kim?", "a": "Shoir"}],
    "Huquq": [{"q": "Oliy qonun nima?", "a": "Konstitutsiya"}]
}

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/admin", response_class=HTMLResponse)
def admin():
    with open("templates/admin.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/start")
def start_test(name: str):
    questions = []
    for subject, qs in tests.items():
        selected = random.sample(qs, 1) # Har fandan 1 tadan savol [cite: 151]
        for q in selected:
            questions.append({"subject": subject, "question": q["q"]})
    random.shuffle(questions) # Aralashtirish [cite: 34, 157]
    return {"student": name, "questions": questions}

@app.post("/check")
async def check_answers(request: Request):
    data = await request.json()
    name, answers = data["name"], data["answers"]
    correct = 0
    # Tekshirish algoritmi [cite: 50-54, 162-175]
    for ans in answers:
        sub = ans["subject"]
        for q in tests[sub]:
            if q["q"] == ans["question"] and q["a"].lower() == ans["answer"].lower():
                correct += 1
    
    percent = (correct / len(answers)) * 100
    summary = "Matematika kuchli" if percent > 70 else "Ko'proq o'qish kerak" # AI xulosasi [cite: 76, 184-187]
    save_result(name, percent, summary) # Bazaga saqlash
    return {"percent": percent, "summary": summary}

@app.get("/get_results")
def get_results():
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('SELECT student_name, total_percent, summary FROM results')
    rows = cursor.fetchall()
    conn.close()
    return rows