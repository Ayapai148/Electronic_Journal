"""
Модуль работы с преподавателем.
"""

from db.database import get_connection


# ============================================================
# ПРОФИЛЬ
# ============================================================

def get_teacher_by_user_id(user_id):
    """Получить профиль преподавателя по id пользователя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, name, surname, patronymic,
                      number, job_title
               FROM teachers
               WHERE user_id = ?""",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ============================================================
# КРУЖКИ
# ============================================================

def get_teacher_clubs(teacher_id):
    """Получить кружки преподавателя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, name, type, schedule, room
               FROM clubs
               WHERE teacher_id = ?
               ORDER BY name""",
            (teacher_id,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# СТУДЕНТЫ
# ============================================================

def get_teacher_students_count(teacher_id):
    """Количество студентов во всех кружках преподавателя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(DISTINCT e.student_id) AS cnt
               FROM enrollments e
               JOIN clubs c ON e.club_id = c.id
               WHERE c.teacher_id = ? AND e.status = 'active'""",
            (teacher_id,)
        )
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_teacher_students(teacher_id, club_id=None):
    """Студенты кружков преподавателя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if club_id:
            cursor.execute(
                """SELECT s.id, s.surname || ' ' || s.name AS fio,
                          s.groups
                   FROM students s
                   JOIN enrollments e ON e.student_id = s.id
                   WHERE e.club_id = ? AND e.status = 'active'
                   ORDER BY s.surname""",
                (club_id,)
            )
        else:
            cursor.execute(
                """SELECT DISTINCT s.id,
                          s.surname || ' ' || s.name AS fio,
                          s.groups
                   FROM students s
                   JOIN enrollments e ON e.student_id = s.id
                   JOIN clubs c ON e.club_id = c.id
                   WHERE c.teacher_id = ? AND e.status = 'active'
                   ORDER BY s.surname""",
                (teacher_id,)
            )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# ЗАНЯТИЯ
# ============================================================

def get_lessons_by_club(club_id):
    """Занятия кружка."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, date, topic, type, hours
               FROM lessons
               WHERE club_id = ?
               ORDER BY date DESC""",
            (club_id,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_teacher_lessons_count(teacher_id):
    """Общее количество занятий преподавателя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(*) AS cnt
               FROM lessons l
               JOIN clubs c ON l.club_id = c.id
               WHERE c.teacher_id = ?""",
            (teacher_id,)
        )
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_teacher_upcoming_lessons(teacher_id, limit=5):
    """Ближайшие занятия преподавателя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT l.date, l.topic, l.type,
                      c.name AS club_name, c.room
               FROM lessons l
               JOIN clubs c ON l.club_id = c.id
               WHERE c.teacher_id = ?
               ORDER BY l.date
               LIMIT ?""",
            (teacher_id, limit)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# ПОСЕЩАЕМОСТЬ
# ============================================================

def get_attendance_by_lesson(lesson_id):
    """Посещаемость занятия с ФИО студентов."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   a.id,
                   s.surname || ' ' || s.name AS student_fio,
                   a.status, a.grade, a.comment
               FROM attendance a
               JOIN students s ON a.student_id = s.id
               WHERE a.lesson_id = ?
               ORDER BY s.surname""",
            (lesson_id,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_teacher_attendance_rate(teacher_id):
    """Процент посещаемости по всем кружкам преподавателя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   COUNT(*) AS total,
                   SUM(CASE WHEN a.status IN ('Присутствовал', 'Опоздал')
                            THEN 1 ELSE 0 END) AS present
               FROM attendance a
               JOIN lessons l ON a.lesson_id = l.id
               JOIN clubs c ON l.club_id = c.id
               WHERE c.teacher_id = ?""",
            (teacher_id,)
        )
        row = cursor.fetchone()
        if not row or row["total"] == 0:
            return None
        return round(row["present"] * 100 / row["total"])
    finally:
        conn.close()


# ============================================================
# ДОСТИЖЕНИЯ
# ============================================================

def get_teacher_students_achievements(teacher_id):
    """Достижения студентов преподавателя."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   s.surname || ' ' || s.name AS student_fio,
                   a.title, a.type, a.level, a.date, a.result
               FROM achievement a
               JOIN students s ON a.student_id = s.id
               WHERE s.id IN (
                   SELECT DISTINCT e.student_id
                   FROM enrollments e
                   JOIN clubs c ON e.club_id = c.id
                   WHERE c.teacher_id = ? AND e.status = 'active'
               )
               ORDER BY a.date DESC""",
            (teacher_id,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# РАСПИСАНИЕ
# ============================================================

def get_teacher_schedule(teacher_id):
    """Расписание преподавателя по дням недели."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT name, schedule, room
               FROM clubs
               WHERE teacher_id = ?
               ORDER BY name""",
            (teacher_id,)
        )
        rows = cursor.fetchall()

        schedule = {
            "ПОНЕДЕЛЬНИК": [],
            "ВТОРНИК": [],
            "СРЕДА": [],
            "ЧЕТВЕРГ": [],
            "ПЯТНИЦА": [],
        }

        day_map = {
            "Пн": "ПОНЕДЕЛЬНИК",
            "Вт": "ВТОРНИК",
            "Ср": "СРЕДА",
            "Чт": "ЧЕТВЕРГ",
            "Пт": "ПЯТНИЦА",
        }

        for row in rows:
            sched = row["schedule"] or ""
            for part in sched.split(","):
                part = part.strip()
                if not part:
                    continue
                tokens = part.split()
                if len(tokens) < 2:
                    continue
                day_short = tokens[0]
                time_str = tokens[1]
                day_full = day_map.get(day_short)
                if not day_full:
                    continue

                schedule[day_full].append({
                    "time": time_str,
                    "club": row["name"],
                    "room": row["room"] or "",
                })

        return schedule
    finally:
        conn.close()