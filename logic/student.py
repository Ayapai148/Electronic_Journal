

from db.database import get_connection


def get_student_by_user_id(user_id):
    """
    Получить профиль студента по id пользователя.

    Args:
        user_id: id из таблицы users

    Returns:
        dict | None: данные студента или None
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, name, surname, patronymic,
                      number, groups, birth_date
               FROM students
               WHERE user_id = ?""",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ============================================================
# 2. КОЛИЧЕСТВО КРУЖКОВ
# ============================================================

def get_clubs_count(student_id):
    """
    Получить количество кружков, на которые записан студент.

    Returns:
        int: количество
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(*) AS cnt
               FROM enrollments
               WHERE student_id = ? AND status = 'active'""",
            (student_id,)
        )
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


# ============================================================
# 3. СРЕДНИЙ БАЛЛ
# ============================================================

def get_average_grade(student_id):
    """
    Получить средний балл студента.

    Считает среднее по колонке grade в attendance.

    Returns:
        float | None: средний балл или None, если оценок нет
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT AVG(grade) AS avg_grade
               FROM attendance
               WHERE student_id = ? AND grade IS NOT NULL""",
            (student_id,)
        )
        row = cursor.fetchone()
        if row and row["avg_grade"] is not None:
            return round(row["avg_grade"], 1)
        return None
    finally:
        conn.close()


# ============================================================
# 4. ПРОЦЕНТ ПОСЕЩАЕМОСТИ
# ============================================================

def get_attendance_rate(student_id):
    """
    Получить процент посещаемости.

    Формула:
        (Присутствовал + Опоздал) / Всего × 100%

    Returns:
        int | None: процент или None, если записей нет
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   COUNT(*) AS total,
                   SUM(CASE WHEN status IN ('Присутствовал', 'Опоздал')
                            THEN 1 ELSE 0 END) AS present
               FROM attendance
               WHERE student_id = ?""",
            (student_id,)
        )
        row = cursor.fetchone()
        if not row or row["total"] == 0:
            return None
        return round(row["present"] * 100 / row["total"])
    finally:
        conn.close()


# ============================================================
# 5. КОЛИЧЕСТВО ДОСТИЖЕНИЙ
# ============================================================

def get_achievements_count(student_id):
    """
    Получить количество достижений студента.

    Returns:
        int: количество
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM achievement WHERE student_id = ?",
            (student_id,)
        )
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


# ============================================================
# 6. БЛИЖАЙШИЕ ЗАНЯТИЯ
# ============================================================

def get_upcoming_lessons(student_id, limit=5):
    """
    Получить ближайшие занятия студента.

    Returns:
        list[dict]: список занятий
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   l.date,
                   l.topic,
                   l.type,
                   c.name AS club_name,
                   c.room,
                   t.surname || ' ' || t.name AS teacher_fio
               FROM lessons l
               JOIN clubs c ON l.club_id = c.id
               JOIN teachers t ON c.teacher_id = t.id
               WHERE c.id IN (
                   SELECT club_id FROM enrollments
                   WHERE student_id = ? AND status = 'active'
               )
               ORDER BY l.date
               LIMIT ?""",
            (student_id, limit)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# 7. РАСПИСАНИЕ
# ============================================================

def get_schedule(student_id):
    """
    Получить расписание студента по клубам.

    Возвращает словарь: {день недели: [(время, клуб, аудитория, преподаватель)]}

    Returns:
        dict: расписание
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   c.name AS club_name,
                   c.schedule,
                   c.room,
                   t.surname || ' ' || t.name AS teacher_fio
               FROM clubs c
               JOIN teachers t ON c.teacher_id = t.id
               WHERE c.id IN (
                   SELECT club_id FROM enrollments
                   WHERE student_id = ? AND status = 'active'
               )
               ORDER BY c.name""",
            (student_id,)
        )
        rows = cursor.fetchall()

        # Группируем по дню недели
        schedule = {
            "ПОНЕДЕЛЬНИК": [],
            "ВТОРНИК": [],
            "СРЕДА": [],
            "ЧЕТВЕРГ": [],
            "ПЯТНИЦА": [],
        }

        for row in rows:
            sched = row["schedule"] or ""
            # Формат: "Пн 15:00-16:30, Ср 15:00-16:30"
            parts = sched.split(",")
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                # Разбираем "Пн 15:00-16:30"
                tokens = part.split()
                if len(tokens) < 2:
                    continue
                day_short = tokens[0]
                time_str = tokens[1] if len(tokens) > 1 else ""

                # Определяем полный день
                day_map = {
                    "Пн": "ПОНЕДЕЛЬНИК",
                    "Вт": "ВТОРНИК",
                    "Ср": "СРЕДА",
                    "Чт": "ЧЕТВЕРГ",
                    "Пт": "ПЯТНИЦА",
                }
                day_full = day_map.get(day_short)
                if not day_full:
                    continue

                schedule[day_full].append({
                    "time": time_str,
                    "club": row["club_name"],
                    "room": row["room"] or "",
                    "teacher": row["teacher_fio"],
                })

        return schedule
    finally:
        conn.close()


# ============================================================
# 8. ОЦЕНКИ
# ============================================================

def get_grades(student_id):
    """
    Получить оценки студента по кружкам.

    Returns:
        list[dict]: список оценок с датой, темой, оценкой
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   l.date,
                   l.topic,
                   a.grade,
                   a.comment,
                   c.name AS club_name,
                   t.surname || ' ' || t.name AS teacher_fio
               FROM attendance a
               JOIN lessons l ON a.lesson_id = l.id
               JOIN clubs c ON l.club_id = c.id
               JOIN teachers t ON c.teacher_id = t.id
               WHERE a.student_id = ? AND a.grade IS NOT NULL
               ORDER BY c.name, l.date DESC""",
            (student_id,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# 9. СПИСОК ПРЕПОДАВАТЕЛЕЙ
# ============================================================

def get_teachers_list():
    """
    Получить список всех преподавателей.

    Returns:
        list[dict]: список преподавателей
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   t.surname || ' ' || t.name || ' ' ||
                   COALESCE(t.patronymic, '') AS fio,
                   t.job_title,
                   COALESCE(GROUP_CONCAT(c.name, ', '), '') AS clubs
               FROM teachers t
               LEFT JOIN clubs c ON c.teacher_id = t.id
               GROUP BY t.id
               ORDER BY t.surname""",
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# 10. СПИСОК ГРУППЫ
# ============================================================

def get_groupmates(group):
    """
    Получить список студентов группы.

    Args:
        group: название группы (например, "ИСП-34")

    Returns:
        list[dict]: список студентов
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   surname || ' ' || name || ' ' ||
                   COALESCE(patronymic, '') AS fio,
                   number,
                   groups
               FROM students
               WHERE groups = ?
               ORDER BY surname""",
            (group,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# 11. ДОСТИЖЕНИЯ
# ============================================================

def get_achievements(student_id):
    """
    Получить достижения студента.

    Returns:
        list[dict]: список достижений
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   title, type, level, place,
                   date, result, points
               FROM achievement
               WHERE student_id = ?
               ORDER BY date DESC""",
            (student_id,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()