import sqlite3

def init_db():
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    
    # 1. Natijalar jadvali
    # MUHIM: total_percent ustuni nomi main.py va admin.html bilan mos bo'lishi shart
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            total_percent REAL,
            summary TEXT,
            subject TEXT DEFAULT 'Umumiy',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Savollar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            question_text TEXT,
            correct_answer TEXT,
            options TEXT,
            difficulty INTEGER
        )
    ''')

    # 3. Kontent jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            data TEXT NOT NULL
        )
    ''')
    
    # Ma'lumotlarni tozalash va yangilash (faqat test rejimida)
    cursor.execute('DELETE FROM questions')
    
    full_questions = [
        ("Informatika", "Sun'iy intellektning qaysi turi inson miyasini modellashtiradi?", "Neyron tarmoqlari", "Algoritm, Neyron tarmoqlari, Ma'lumotlar bazasi, Protsessor", 3),
        ("Informatika", "Individuallashtirilgan ta'limda AI-ning asosiy vazifasi nima?", "Moslashuvchanlik", "Tezlik, Moslashuvchanlik, Xotira, Dizayn", 2),
        ("Informatika", "Python-da 'print' funksiyasi nima vazifani bajaradi?", "Chiqarish", "Kiritish, Chiqarish, Saqlash, O'chirish", 1),
        ("Matematika", "Kvadratning yuzi 25 bo'lsa, uning tomonini toping.", "5", "4, 5, 6, 10", 1),
        ("Matematika", "Sinus 90 gradusda nechaga teng?", "1", "0, 1, 0.5, -1", 2)
    ]
    
    cursor.executemany('''
        INSERT INTO questions (subject, question_text, correct_answer, options, difficulty)
        VALUES (?, ?, ?, ?, ?)
    ''', full_questions)

    cursor.execute('DELETE FROM content')
    sample_content = [
        ("Informatika", "reels", "AI qanday o'rganadi?", "2ePf9rue1Ao"), 
        ("Informatika", "lesson", "Neyron tarmoqlari asoslari", "kKKM8Y-u7ds"),
        ("Matematika", "reels", "Pifagor teoremasi 60 soniyada", "Z0p9O_V6L_w"),
        ("Matematika", "lesson", "Integral tushunchasi", "j_N6O6O2C_0")
    ]
    cursor.executemany('INSERT INTO content (subject, content_type, title, data) VALUES (?, ?, ?, ?)', sample_content)
    
    conn.commit()
    conn.close()

def save_result(name, percent, summary, subject="Umumiy"):
    try:
        conn = sqlite3.connect('edu_platform.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO results (student_name, total_percent, summary, subject) 
            VALUES (?, ?, ?, ?)
        ''', (name, percent, summary, subject))
        conn.commit()
        conn.close()
        print(f"Natija saqlandi: {name} - {percent}%")
    except Exception as e:
        print(f"Bazada saqlashda xatolik: {e}")

if __name__ == "__main__":
    init_db()
    print("BMI Bazasi: Muvaffaqiyatli yangilandi!")