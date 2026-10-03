import hashlib 
from db.database import get_connection

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(login: str, password: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE login = ? AND password = ?",
            (login, hash_password(password))
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def _register_user(fio, login, password, role, group="", direction="", email=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cursor.fetchone():
            return False

        cursor.execute(
            "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
            (login, hash_password(password), role)
        )
        user_id = cursor.lastrowid

        parts = fio.split()
        surname = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else ""
        patronymic = parts[2] if len(parts) > 2 else ""

        if role == " student":
            cursor.execute(
                """INSERT INTO students
                (name, surname, patronymic, group, user_id)
                VALUES (?, ?, ?, ?, ?)""",
                (name, surname, patronymic, group, user_id)
            )
        elif role == "teacher":
            cursor.execute(
                """INSERT INTO teachers
                (name, surname, patronymic, direction, user_id)
                VALUES (?, ?, ?, ?, ?)""",
                (name, surname, patronymic, group, user_id)
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка {e}")
        return False
    finally:
        conn.close()