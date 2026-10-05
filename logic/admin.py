"""
Модуль работы с администратором.

Функции для получения статистики, списка пользователей,
управления пользователями, отчётов.
"""

import hashlib
from db.database import get_connection


# ============================================================
# СТАТИСТИКА
# ============================================================

def get_users_count():
    """Общее количество пользователей."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM users")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_students_count():
    """Количество студентов."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM students")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_teachers_count():
    """Количество преподавателей."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM teachers")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_clubs_count():
    """Количество кружков и секций."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM clubs")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================

def get_all_users():
    """
    Все пользователи с ФИО и ролью.

    Returns:
        list[dict]: id, login, role, fio, create_date
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                u.id,
                u.login,
                u.role,
                u.create_date,
                COALESCE(
                    (SELECT s.surname || ' ' || s.name
                     FROM students s WHERE s.user_id = u.id),
                    (SELECT t.surname || ' ' || t.name
                     FROM teachers t WHERE t.user_id = u.id),
                    '—'
                ) AS fio
            FROM users u
            ORDER BY u.id
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def delete_user(user_id):
    """Удалить пользователя по id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def create_user(login, password, role):
    """Создать нового пользователя (без профиля)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверка логина
        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cursor.fetchone():
            return False

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
            (login, password_hash, role)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()


# ============================================================
# ОТЧЁТЫ
# ============================================================

def get_clubs_report():
    """
    Сводка по кружкам: количество студентов, средний балл, посещаемость.

    Returns:
        list[dict]: club, teacher, students, avg_grade, attendance
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                c.name AS club,
                COALESCE(t.surname || ' ' || t.name, '—') AS teacher,
                COUNT(DISTINCT e.student_id) AS students,
                ROUND(COALESCE(AVG(a.grade), 0), 1) AS avg_grade,
                CASE
                    WHEN COUNT(at.id) > 0
                    THEN ROUND(100.0 * SUM(
                        CASE WHEN at.status IN ('Присутствовал', 'Опоздал')
                        THEN 1 ELSE 0 END) / COUNT(at.id))
                    ELSE 0
                END AS attendance
            FROM clubs c
            LEFT JOIN teachers t ON c.teacher_id = t.id
            LEFT JOIN enrollments e ON c.id = e.club_id AND e.status = 'active'
            LEFT JOIN lessons l ON c.id = l.club_id
            LEFT JOIN attendance a ON a.lesson_id = l.id
            LEFT JOIN attendance at ON at.lesson_id = l.id
            GROUP BY c.id
            ORDER BY c.name
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# ПОСЛЕДНИЕ ДЕЙСТВИЯ (заглушка — логов пока нет)
# ============================================================

def get_recent_actions(limit=5):
    """
    Последние действия пользователей из audit_log.

    Returns:
        list[dict]: date, user, action
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   create_date AS date,
                   user_login AS user,
                   action || CASE
                       WHEN details IS NOT NULL AND details != ''
                       THEN ': ' || details
                       ELSE ''
                   END AS action
               FROM audit_log
               ORDER BY id DESC
               LIMIT ?""",
            (limit,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

# ============================================================
# СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ С ПРОФИЛЕМ
# ============================================================
def log_action(user_id, user_login, action, details=""):
    """
    Записать действие в audit_log.

    Args:
        user_id: id пользователя
        user_login: логин пользователя
        action: краткое действие («Добавлен пользователь»)
        details: подробности («Иванов Иван, роль: teacher»)
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO audit_log
               (user_id, user_login, action, details)
               VALUES (?, ?, ?, ?)""",
            (user_id, user_login, action, details)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Ошибка записи лога: {e}")
    finally:
        conn.close()

def create_user_with_profile(fio, login, password, role,
                             group="", direction="", admin=None):
    """
    Создать пользователя вместе с профилем (студент/преподаватель).

    Args:
        fio: ФИО одной строкой
        login: логин
        password: пароль (открытый)
        role: student / teacher / admin
        group: группа (для студента)
        direction: направление (для преподавателя)

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверяем логин
        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cursor.fetchone():
            return False

        # Хешируем пароль
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Создаём пользователя
        cursor.execute(
            "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
            (login, password_hash, role)
        )
        user_id = cursor.lastrowid

        # Разбираем ФИО
        parts = fio.split()
        surname = parts[0] if len(parts) > 0 else ""
        name = parts[1] if len(parts) > 1 else ""
        patronymic = parts[2] if len(parts) > 2 else ""

        # Создаём профиль
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
        # Для admin профиль не нужен

        conn.commit()
        if admin:
            log_action(
                user_id=admin.get("id"),
                user_login=admin.get("login", "—"),
                action="Добавлен пользователь",
                details=f"{fio}, роль: {role}"
            )

        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка создания пользователя: {e}")
        return False
    finally:
        conn.close()
    
    