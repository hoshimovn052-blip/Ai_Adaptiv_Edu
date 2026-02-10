import sqlite3

def init_db():
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    
    # 1. Natijalar jadvali
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
    
    # --- SAVOLLAR BAZASINI BOYITISH ---
    cursor.execute('DELETE FROM questions') # Eski savollarni tozalab, yangilarini yozish uchun
    
    full_questions = [
        # INFORMATIKA (Darajalar: 1-Oson, 2-O'rta, 3-Qiyin)
        ("Informatika", "Kompyuterning miyasi nima?", "CPU", "RAM, CPU, Monitor, Klaviatura", 1),
        ("Informatika", "Algoritm nima?", "Ketma-ketlik", "O'yin, Ketma-ketlik, Qurilma, Dastur", 1),
        ("Informatika", "Python-da ro'yxat qaysi qavs bilan yaratiladi?", "[]", "(), {}, [], <>", 1),
        ("Informatika", "Sun'iy intellekt tushunchasini fanga kim kiritgan?", "Jon Makkarti", "Alan Tyuring, Jon Makkarti, Bill Geyts, Stiv Jobs", 2),
        ("Informatika", "Ma'lumotlar bazasini boshqarish tili?", "SQL", "HTML, CSS, SQL, PHP", 2),
        ("Informatika", "HTTP porti raqami nechaga teng?", "80", "21, 80, 443, 3306", 2),
        ("Informatika", "Murakkab neyron tarmoqlari qayerda ishlatiladi?", "Deep Learning", "Word, Deep Learning, Excel, Paint", 3),
        ("Informatika", "O(n log n) qaysi saralash algoritmiga tegishli?", "Merge Sort", "Bubble Sort, Merge Sort, Linear Search, Insertion Sort", 3),
        ("Informatika", "Blockchain texnologiyasining asosiy ustunligi?", "Markazlashmaganlik", "Tezlik, Markazlashmaganlik, Narx, Dizayn", 3),
        
        # MATEMATIKA
        ("Matematika", "2 + 2 * 2 necha bo'ladi?", "6", "8, 6, 4, 10", 1),
        ("Matematika", "Uchburchakning ichki burchaklari yig'indisi?", "180", "90, 180, 270, 360", 1),
        ("Matematika", "5 ning faktoriali (5!) nechaga teng?", "120", "100, 120, 150, 25", 2),
        ("Matematika", "Pifagor teoremasini toping.", "a2 + b2 = c2", "a+b=c, a2 + b2 = c2, a*b=c, Sin(x)=1", 2),
        ("Matematika", "Logarifm log2(8) nechaga teng?", "3", "2, 3, 4, 8", 2),
        ("Matematika", "Integral (x) dx nima?", "x2/2 + C", "x, x2, x2/2 + C, 1", 3),
        ("Matematika", "Kvadrat tenglamaning diskriminant formulasi?", "D = b2 - 4ac", "D = b-4ac, D = b2 - 4ac, D = a2+b2, D = 2b-a", 3),

        # INGLIZ TILI
        ("Ingliz tili", "Cat so'zining o'zbekcha tarjimasi?", "Mushuk", "It, Mushuk, Ot, Fil", 1),
        ("Ingliz tili", "Go so'zining o'tgan zamon shakli?", "Went", "Goes, Went, Gone, Going", 2),
        ("Ingliz tili", "If I ___ rich, I would travel.", "were", "am, was, were, be", 3),
        
        # FIZIKA
        ("Fizika", "Erkin tushish tezlanishi (g) qiymati?", "9.8 m/s2", "10, 9.8 m/s2, 5, 12", 1),
        ("Fizika", "Nyutonning 2-qonuni?", "F = ma", "E = mc2, F = ma, P = UI, V = IR", 2),
        ("Fizika", "Yorug'lik tezligi qancha?", "300,000 km/s", "100, 300,000 km/s, 1000, 50,000", 3)
    ]
    
    cursor.executemany('''
        INSERT INTO questions (subject, question_text, correct_answer, options, difficulty)
        VALUES (?, ?, ?, ?, ?)
    ''', full_questions)

    # --- MULTIMEDIA KONTENTINI BOYITISH ---
    cursor.execute('DELETE FROM content')
    sample_content = [
        ("Informatika", "video", "Sun'iy intellekt darsi", "https://www.youtube.com/embed/2ePf9rue1Ao"),
        ("Informatika", "news", "AI yangiliklari", "O'zbekistonda AI-Edu platformasi ishga tushirildi."),
        ("Matematika", "video", "Kvadrat tenglamalar", "https://www.youtube.com/embed/Z0p9O_V6L_w"),
        ("Ingliz tili", "video", "Grammatika darsi", "https://www.youtube.com/embed/j_N6O6O2C_0"),
        ("Fizika", "news", "Kvant fizikasi", "Olimlar kvant teleportatsiyasi bo'yicha yangi yutuqqa erishdilar.")
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
    print("Baza muvaffaqiyatli boyitildi! Har bir fan bo'yicha savollar va darajalar kiritildi.")