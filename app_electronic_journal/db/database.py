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
        CREAETE TABLE IF NOT EXITS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            create_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
                   """)
    #Студенты
    cursor.execute("""
        CREATE TABLE IF NOT EXITS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            surname TEXT UNIQUE NOT NULL,
            patronymic TEXT UNIQUE NOT NULL,
            number TEXT,
            groups INTEGER,
            brith_date TEXT
        )
                   """)
    cursor.execute("""
        CREATE TABLE IF NOT EXITS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT UNIQUE NOT NULL,
            surname TEXT UNIQUE NOT NULL,
            patronymic TEXT UNIQUE NOT NULL,
            number TEXT,
            job_title TEXT
        )
                   """)
    cursor.execute("""
        CREATE TABLE IF NOTE EXITS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            topic TEXT UNIQUE NOT NULL,
            type TEXT UNIQUE NOT NULL,
            hours INTEGER
        )
                   """)
    conn.commit()
    conn.close()
    