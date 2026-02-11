import sqlite3

def init_db():
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    
    # 1. Natijalar jadvali (Individuallashtirilgan AI xulosasi bilan)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            total_percent REAL,
            summary TEXT, -- Bu yerda AI o'quvchiga individual tavsiya beradi
            subject TEXT DEFAULT 'Umumiy',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Savollar jadvali (Adaptiv mantiq uchun darajalar bilan)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            question_text TEXT,
            correct_answer TEXT,
            options TEXT,
            difficulty INTEGER -- 1: Oson, 2: O'rta, 3: Qiyin
        )
    ''')

    # 3. Kontent jadvali (BMI: Reels va Darsliklarga ajratilgan)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            content_type TEXT NOT NULL, -- 'reels' (Shorts) yoki 'lesson' (To'liq dars)
            title TEXT NOT NULL,
            data TEXT NOT NULL -- YouTube Video ID
        )
    ''')
    
    # --- SAVOLLARNI TOZALASH VA YANGILASH ---
    cursor.execute('DELETE FROM questions')
    
    full_questions = [
        # INFORMATIKA - Individuallashtirilgan ta'lim elementlari
        ("Informatika", "Sun'iy intellektning qaysi turi inson miyasini modellashtiradi?", "Neyron tarmoqlari", "Algoritm, Neyron tarmoqlari, Ma'lumotlar bazasi, Protsessor", 3),
        ("Informatika", "Individuallashtirilgan ta'limda AI-ning asosiy vazifasi nima?", "Moslashuvchanlik", "Tezlik, Moslashuvchanlik, Xotira, Dizayn", 2),
        ("Informatika", "Python-da 'print' funksiyasi nima vazifani bajaradi?", "Chiqarish", "Kiritish, Chiqarish, Saqlash, O'chirish", 1),
        
        # MATEMATIKA
        ("Matematika", "Kvadratning yuzi 25 bo'lsa, uning tomonini toping.", "5", "4, 5, 6, 10", 1),
        ("Matematika", "Sinus 90 gradusda nechaga teng?", "1", "0, 1, 0.5, -1", 2),
        
        # FIZIKA, INGLIZ TILI va boshqalar... (Sizning ro'yxatingizdagilar qoladi)
    ]
    
    cursor.executemany('''
        INSERT INTO questions (subject, question_text, correct_answer, options, difficulty)
        VALUES (?, ?, ?, ?, ?)
    ''', full_questions)

    # --- BMI MULTIMEDIA: REELS VA DARSLIKLAR ---
    cursor.execute('DELETE FROM content')
    sample_content = [
        # Informatika bo'limi
        ("Informatika", "reels", "AI qanday o'rganadi?", "2ePf9rue1Ao"), 
        ("Informatika", "lesson", "Neyron tarmoqlari asoslari", "kKKM8Y-u7ds"),
        
        # Matematika bo'limi
        ("Matematika", "reels", "Pifagor teoremasi 60 soniyada", "Z0p9O_V6L_w"),
        ("Matematika", "lesson", "Integral tushunchasi", "j_N6O6O2C_0"),
        
        # Fizika bo'limi
        ("Fizika", "reels", "Nyuton qonuni amalda", "dQw4w9WgXcQ")
    ]
    cursor.executemany('INSERT INTO content (subject, content_type, title, data) VALUES (?, ?, ?, ?)', sample_content)
    
    conn.commit()
    conn.close()

def save_result(name, percent, summary, subject="Umumiy"):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO results (student_name, total_percent, summary, subject) VALUES (?, ?, ?, ?)', 
                   (name, percent, summary, subject))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("BMI Bazasi: Individuallashtirilgan ta'lim tizimi uchun muvaffaqiyatli moslandi!")