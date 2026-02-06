import sqlite3

def init_db():
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    # Natijalarni saqlash uchun jadval yaratish [cite: 101]
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            total_percent REAL,
            summary TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_result(name, percent, summary):
    conn = sqlite3.connect('edu_platform.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO results (student_name, total_percent, summary) VALUES (?, ?, ?)', 
                   (name, percent, summary))
    conn.commit()
    conn.close()