"""
Модуль авторизации и регистрации.
Соответствует ТЗ ЭЖКСР.
"""

import hashlib
from db.database import get_connection


# ============================================================
# ХЕШИРОВАНИЕ ПАРОЛЯ
# ============================================================

def hash_password(password: str) -> str:
    """
    Хеширование пароля через SHA-256.

    Args:
        password: пароль в открытом виде

    Returns:
        str: hex-строка хеша
    """
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
# АВТОРИЗАЦИЯ
# ============================================================

def authenticate(login: str, password: str):
    """
    Проверить логин и пароль.

    Returns:
        dict | None: данные пользователя или None
    """
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


# ============================================================
# РЕГИСТРАЦИЯ СТУДЕНТА
# ============================================================

def register_student(fio: str, login: str, password: str,
                     group: str = "", email: str = ""):
    """
    Зарегистрировать студента.

    Args:
        fio: ФИО одной строкой
        login: логин
        password: пароль
        group: группа (например, «ИСП-34»)
        email: электронная почта

    Returns:
        bool: True если успешно
    """
    return _register_user(
        fio=fio,
        login=login,
        password=password,
        role="student",
        group=group,
        email=email,
        direction=""
    )


# ============================================================
# РЕГИСТРАЦИЯ ПРЕПОДАВАТЕЛЯ
# ============================================================

def register_teacher(fio: str, login: str, password: str,
                     direction: str = "", email: str = ""):
    """
    Зарегистрировать преподавателя.

    Args:
        fio: ФИО одной строкой
        login: логин
        password: пароль
        direction: направление (например, «Информатика»)
        email: электронная почта

    Returns:
        bool: True если успешно
    """
    return _register_user(
        fio=fio,
        login=login,
        password=password,
        role="teacher",
        group="",
        email=email,
        direction=direction
    )


# ============================================================
# ОБЩАЯ ФУНКЦИЯ РЕГИСТРАЦИИ (приватная)
# ============================================================

def _register_user(fio, login, password, role,
                   group="", email="", direction=""):
    """
    Общая логика регистрации.

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 1. Проверяем, что логин свободен
        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cursor.fetchone():
            return False

        # 2. Создаём пользователя
        cursor.execute(
            "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
            (login, hash_password(password), role)
        )
        user_id = cursor.lastrowid

        # 3. Разбираем ФИО
        parts = fio.split()
        surname = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else ""
        patronymic = parts[2] if len(parts) > 2 else ""

        # 4. Создаём профиль
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