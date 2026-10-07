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


def register_student(fio, login, password, group="", email=""):
    return _register_user(
        fio=fio, login=login, password=password,
        role="student", group=group, email=email
    )


def register_teacher(fio, login, password, direction="", email=""):
    return _register_user(
        fio=fio, login=login, password=password,
        role="teacher", direction=direction, email=email
    )


def _register_user(fio, login, password, role,
                   group="", direction="", email=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cursor.fetchone():
            return False

        cursor.execute(
            """INSERT INTO users (login, password, role, email)
               VALUES (?, ?, ?, ?)""",
            (login, hash_password(password), role, email)
        )
        user_id = cursor.lastrowid

        parts = fio.split()
        surname = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else ""
        patronymic = parts[2] if len(parts) > 2 else ""

        if role == "student":
            cursor.execute(
                """INSERT INTO students
                   (name, surname, patronymic, groups, user_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, surname, patronymic, group, user_id)
            )
        elif role == "teacher":
            cursor.execute(
                """INSERT INTO teachers
                   (name, surname, patronymic, job_title, user_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, surname, patronymic, direction, user_id)
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка регистрации: {e}")
        return False
    finally:
        conn.close()


def find_user_by_email(email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, login, role FROM users WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def generate_reset_code():
    import random
    return str(random.randint(100000, 999999))


def save_reset_code(user_id, email, code):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE password_reset SET used = 1 WHERE email = ? AND used = 0",
            (email,)
        )

        cursor.execute(
            """INSERT INTO password_reset (user_id, email, code)
               VALUES (?, ?, ?)""",
            (user_id, email, code)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка сохранения кода: {e}")
        return False
    finally:
        conn.close()


def verify_reset_code(email, code):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_id FROM password_reset
               WHERE email = ? AND code = ? AND used = 0
               ORDER BY id DESC LIMIT 1""",
            (email, code)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_password(user_id, new_password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hash_password(new_password), user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def mark_code_used(reset_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE password_reset SET used = 1 WHERE id = ?",
            (reset_id,)
        )
        conn.commit()
        return True
    finally:
        conn.close()


def send_email(to, subject, body):
    print()
    print("=" * 60)
    print(f"[EMAIL] Кому:     {to}")
    print(f"[EMAIL] Тема:     {subject}")
    print(f"[EMAIL] Текст:    {body}")
    print("=" * 60)
    print()
    return True