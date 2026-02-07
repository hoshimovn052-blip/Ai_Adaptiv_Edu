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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Savollar jadvali (Adaptive qiyinlik darajasi bilan)
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
    
    # Bazada savollar bor-yo'qligini tekshirish
    cursor.execute('SELECT COUNT(*) FROM questions')
    if cursor.fetchone()[0] == 0:
        # Savollar ro'yxati
        questions = [
            ("Matematika", "15 ning kvadrati nechaga teng?", "225", "200, 225, 250, 125", 1),
            ("Matematika", "Agar x + 15 = 40 bo'lsa, x ni toping.", "25", "20, 25, 30, 35", 2),
            ("Matematika", "Uchburchakning yuzini topish formulasi qaysi?", "S = (a*h)/2", "S = a*b, S = (a*h)/2, S = 2*a*b, S = a+b", 3),
            ("Informatika", "Kompyuterning asosiy xotirasi nima deb ataladi?", "RAM", "CPU, RAM, HDD, SSD", 1),
            ("Informatika", "Python tilida ekranga chiqarish buyrug'i qaysi?", "print()", "output(), log(), write(), print()", 1),
            ("Informatika", "Sun'iy intellektning asosiy yo'nalishi nima?", "Machine Learning", "Hardware, Machine Learning, Networking, Office", 3),
            ("Fizika", "Tezlikning o'lchov birligi nima?", "m/s", "kg, m/s, J, N", 1),
            ("Fizika", "Nyutonning ikkinchi qonuni formulasi?", "F = m*a", "F = m*v, F = m*a, E = mc^2, P = F/S", 2),
            ("Fizika", "Yorug'lik tezligi taxminan qancha?", "300,000 km/s", "100,000 km/s, 300,000 km/s, 500,000 km/s, 1 mln km/s", 3),
            ("Ingliz tili", "I ___ a student.", "am", "is, are, am, be", 1),
            ("Ingliz tili", "Choose the past simple of 'GO'.", "went", "gone, goes, went, going", 2),
            ("Ingliz tili", "Identify the synonym for 'INTELLIGENT'.", "smart", "slow, smart, happy, brave", 3),
            ("Kimyo", "Suvning kimyoviy formulasi?", "H2O", "CO2, H2O, O2, NaCl", 1),
            ("Kimyo", "Osh tuzining kimyoviy nomi?", "NaCl", "NaOH, NaCl, HCl, KCl", 2),
            ("Kimyo", "Mendeleyev davriy jadvalida birinchi element?", "Vodorod", "Kislorod, Oltin, Vodorod, Geliy", 1)
        ]
        cursor.executemany('''
            INSERT INTO questions (subject, question_text, correct_answer, options, difficulty)
            VALUES (?, ?, ?, ?, ?)
        ''', questions)
    
    conn.commit()
    conn.close()

def save_result(name, percent, summary):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO results (student_name, total_percent, summary) VALUES (?, ?, ?)', 
                   (name, percent, summary))
    conn.commit()
    conn.close()