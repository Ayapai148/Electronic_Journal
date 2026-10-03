import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "ejksr.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    #пользователи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            create_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
                   """)
    #Студенты
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            surname TEXT UNIQUE NOT NULL,
            patronymic TEXT UNIQUE NOT NULL,
            number TEXT,
            groups INTEGER,
            brith_date TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
                   """)
    #Преподаватели
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT UNIQUE NOT NULL,
            surname TEXT UNIQUE NOT NULL,
            patronymic TEXT UNIQUE NOT NULL,
            number TEXT,
            job_title TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
                   """)
    #кружки 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            topic TEXT UNIQUE NOT NULL,
            type TEXT UNIQUE NOT NULL,
            hours INTEGER,
            club_id INTEGER,
            FOREIGN KEY (club_id) REFERENCES clubs(id)
        )
                   """)
    #секции
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            shelude TEXT,
            direction TEXT,
            room TEXT,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        ) 
                    """)
    #посещаемость
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            cause TEXT,
            lesson_id INTEGER,
            student_id INTEGER,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)
    #зачисления
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enroll_date TEXT,
            status TEXT,
            student_id INTEGER,
            club_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
        )
    """)
    #портфолио студента
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER,
            student_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
if __name__ == "__main__":
    init_db()
    print("базы данных создана")