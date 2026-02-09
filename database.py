import sqlite3

def init_db():
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    
    # 1. Natijalar jadvali (Subject ustuni qo'shildi)
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

    # 3. Fanlar uchun kontent jadvali (Video va Yangiliklar)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            content_type TEXT NOT NULL, -- 'video' yoki 'news'
            title TEXT NOT NULL,
            data TEXT NOT NULL -- URL yoki matn
        )
    ''')
    
    # Bazada savollar bor-yo'qligini tekshirish va namunaviy ma'lumotlar qo'shish
    cursor.execute('SELECT COUNT(*) FROM questions')
    if cursor.fetchone()[0] == 0:
        questions = [
            ("Matematika", "15 ning kvadrati nechaga teng?", "225", "200, 225, 250, 125", 1),
            ("Matematika", "Agar x + 15 = 40 bo'lsa, x ni toping.", "25", "20, 25, 30, 35", 2),
            ("Informatika", "Kompyuterning asosiy xotirasi nima deb ataladi?", "RAM", "CPU, RAM, HDD, SSD", 1),
            ("Informatika", "Sun'iy intellektning asosiy yo'nalishi nima?", "Machine Learning", "Hardware, Machine Learning, Networking, Office", 3),
            ("Fizika", "Tezlikning o'lchov birligi nima?", "m/s", "kg, m/s, J, N", 1),
            ("Ingliz tili", "I ___ a student.", "am", "is, are, am, be", 1),
            ("Kimyo", "Suvning kimyoviy formulasi?", "H2O", "CO2, H2O, O2, NaCl", 1)
        ]
        cursor.executemany('''
            INSERT INTO questions (subject, question_text, correct_answer, options, difficulty)
            VALUES (?, ?, ?, ?, ?)
        ''', questions)

    # Namunaviy kontentlar (Video va Yangiliklar) qo'shish
    cursor.execute('SELECT COUNT(*) FROM content')
    if cursor.fetchone()[0] == 0:
        sample_content = [
            ("Informatika", "video", "Sun'iy intellekt asoslari", "https://www.youtube.com/embed/2ePf9rue1Ao"),
            ("Matematika", "news", "Matematika olamidagi yangilik", "Yaqinda yangi eng katta tub son topildi."),
            ("Fizika", "video", "Nyuton qonunlari", "https://www.youtube.com/embed/kKKM8Y-u7ds")
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

# Dastur ishga tushganda bazani tayyorlash
if __name__ == "__main__":
    init_db()
    print("Baza muvaffaqiyatli yangilandi va birlashtirildi!")