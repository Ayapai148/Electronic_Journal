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
# ============================================================
# КРУЖКИ (для преподавателя)
# ============================================================

def get_teacher_clubs_full(teacher_id):
    """
    Кружки преподавателя с полной информацией.

    Returns:
        list[dict]: id, name, type, schedule, room
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, type, schedule, room
            FROM clubs
            WHERE teacher_id = ?
            ORDER BY name
        """, (teacher_id,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def create_teacher_club(teacher_id, name, type_, schedule, room):
    """
    Создать кружок от имени преподавателя.

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO clubs (name, type, teacher_id, schedule, room)
               VALUES (?, ?, ?, ?, ?)""",
            (name, type_, teacher_id, schedule, room)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()


def update_teacher_club(club_id, teacher_id, name, type_, schedule, room):
    """
    Обновить свой кружок.
    Проверяет, что кружок принадлежит этому преподавателю.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверка принадлежности
        cursor.execute(
            "SELECT id FROM clubs WHERE id = ? AND teacher_id = ?",
            (club_id, teacher_id)
        )
        if not cursor.fetchone():
            return False

        cursor.execute(
            """UPDATE clubs
               SET name = ?, type = ?, schedule = ?, room = ?
               WHERE id = ?""",
            (name, type_, schedule, room, club_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()


def delete_teacher_club(club_id, teacher_id):
    """
    Удалить свой кружок.
    Проверяет, что кружок принадлежит этому преподавателю.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверка принадлежности
        cursor.execute(
            "SELECT id FROM clubs WHERE id = ? AND teacher_id = ?",
            (club_id, teacher_id)
        )
        if not cursor.fetchone():
            return False

        cursor.execute("DELETE FROM clubs WHERE id = ?", (club_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# ============================================================
# ЗАПИСЬ СТУДЕНТОВ В КРУЖОК
# ============================================================

def get_all_students():
    """
    Все студенты для выбора.

    Returns:
        list[dict]: id, fio, groups, number
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                id,
                surname || ' ' || name AS fio,
                groups,
                number
            FROM students
            ORDER BY surname, name
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_enrolled_students(club_id):
    """
    Студенты, уже записанные в кружок.

    Returns:
        list[int]: список student_id
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT student_id
               FROM enrollments
               WHERE club_id = ? AND status = 'active'""",
            (club_id,)
        )
        return [row["student_id"] for row in cursor.fetchall()]
    finally:
        conn.close()


def enroll_student(club_id, student_id):
    """
    Записать студента в кружок.

    Если уже записан — ничего не делает.

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверка: уже записан?
        cursor.execute(
            """SELECT id FROM enrollments
               WHERE club_id = ? AND student_id = ?""",
            (club_id, student_id)
        )
        if cursor.fetchone():
            return True

        # Записываем
        cursor.execute(
            """INSERT INTO enrollments
               (student_id, club_id, enroll_date, status)
               VALUES (?, ?, date('now'), 'active')""",
            (student_id, club_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка записи студента: {e}")
        return False
    finally:
        conn.close()


def unenroll_student(club_id, student_id):
    """
    Отчислить студента из кружка.

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """DELETE FROM enrollments
               WHERE club_id = ? AND student_id = ?""",
            (club_id, student_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка отчисления: {e}")
        return False
    finally:
        conn.close()


def save_club_enrollments(club_id, student_ids):
    """
    Сохранить список студентов кружка.

    Сравнивает текущий список с новым:
    - кого нет — записывает;
    - кого убрали — отчисляет.

    Args:
        club_id: id кружка
        student_ids: список id студентов (кто должен быть записан)

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Текущие записи
        cursor.execute(
            "SELECT student_id FROM enrollments WHERE club_id = ?",
            (club_id,)
        )
        current = {row["student_id"] for row in cursor.fetchall()}
        new = set(student_ids)

        # Кого добавить
        to_add = new - current
        # Кого убрать
        to_remove = current - new

        for sid in to_add:
            cursor.execute(
                """INSERT INTO enrollments
                   (student_id, club_id, enroll_date, status)
                   VALUES (?, ?, date('now'), 'active')""",
                (sid, club_id)
            )

        for sid in to_remove:
            cursor.execute(
                "DELETE FROM enrollments WHERE club_id = ? AND student_id = ?",
                (club_id, sid)
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка сохранения: {e}")
        return False
    finally:
        conn.close()

# ============================================================
# ЖУРНАЛ: студенты, занятия, оценки
# ============================================================

def get_students_by_club(club_id):
    """
    Студенты, записанные в кружок.

    Returns:
        list[dict]: id, fio, groups
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                s.id,
                s.surname || ' ' || s.name AS fio,
                s.groups
            FROM students s
            JOIN enrollments e ON e.student_id = s.id
            WHERE e.club_id = ? AND e.status = 'active'
            ORDER BY s.surname, s.name
        """, (club_id,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_lessons_by_club_sorted(club_id):
    """
    Занятия кружка в хронологическом порядке (для журнала).

    Returns:
        list[dict]: id, date, topic
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, topic
            FROM lessons
            WHERE club_id = ?
            ORDER BY date ASC
        """, (club_id,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_attendance_map(club_id):
    """
    Карта посещаемости и оценок кружка.

    Returns:
        dict: {(student_id, lesson_id): {"grade": 5, "status": "Присутствовал", "attendance_id": 1}}
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.id AS attendance_id,
                a.student_id,
                a.lesson_id,
                a.grade,
                a.status,
                a.comment
            FROM attendance a
            JOIN lessons l ON a.lesson_id = l.id
            WHERE l.club_id = ?
        """, (club_id,))

        result = {}
        for row in cursor.fetchall():
            key = (row["student_id"], row["lesson_id"])
            result[key] = {
                "attendance_id": row["attendance_id"],
                "grade": row["grade"],
                "status": row["status"],
                "comment": row["comment"],
            }
        return result
    finally:
        conn.close()


def update_grade(lesson_id, student_id, grade, comment="", status="Присутствовал"):
    """
    Обновить или создать оценку студента за занятие.

    Args:
        lesson_id: id занятия
        student_id: id студента
        grade: оценка (2-5) или None
        comment: примечание
        status: статус посещаемости

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверяем, есть ли запись
        cursor.execute("""
            SELECT id FROM attendance
            WHERE lesson_id = ? AND student_id = ?
        """, (lesson_id, student_id))

        row = cursor.fetchone()

        if row:
            # Обновляем
            cursor.execute("""
                UPDATE attendance
                SET grade = ?, comment = ?, status = ?
                WHERE id = ?
            """, (grade, comment, status, row["id"]))
        else:
            # Создаём
            cursor.execute("""
                INSERT INTO attendance
                (lesson_id, student_id, status, cause, grade, comment)
                VALUES (?, ?, ?, '', ?, ?)
            """, (lesson_id, student_id, status, grade, comment))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка обновления оценки: {e}")
        return False
    finally:
        conn.close()


def create_lesson(club_id, date, topic, type_="Практика", hours=2):
    """
    Создать занятие.

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lessons (date, topic, type, hours, club_id)
            VALUES (?, ?, ?, ?, ?)
        """, (date, topic, type_, hours, club_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка создания занятия: {e}")
        return False
    finally:
        conn.close()


def delete_lesson(lesson_id):
    """Удалить занятие (все оценки тоже удалятся через CASCADE)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# ============================================================
# СТАТИСТИКА ПО СТУДЕНТАМ
# ============================================================

def get_student_averages(club_id):
    """
    Средний балл и итоговая оценка каждого студента кружка.

    Returns:
        dict: {student_id: {"avg": 4.5, "final": 5}}
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.student_id,
                AVG(a.grade) AS avg_grade,
                COUNT(a.grade) AS grades_count
            FROM attendance a
            JOIN lessons l ON a.lesson_id = l.id
            WHERE l.club_id = ?
              AND a.grade IS NOT NULL
            GROUP BY a.student_id
        """, (club_id,))

        result = {}
        for row in cursor.fetchall():
            avg = row["avg_grade"] or 0
            result[row["student_id"]] = {
                "avg": round(avg, 2),
                "final": round(avg),
            }
        return result
    finally:
        conn.close()
# ============================================================
# ДОСТИЖЕНИЯ (для преподавателя)
# ============================================================

def get_teacher_students(teacher_id):
    """
    Все студенты кружков преподавателя (для выбора).

    Returns:
        list[dict]: id, fio, groups
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                s.id,
                s.surname || ' ' || s.name AS fio,
                s.groups
            FROM students s
            JOIN enrollments e ON e.student_id = s.id
            JOIN clubs c ON e.club_id = c.id
            WHERE c.teacher_id = ? AND e.status = 'active'
            ORDER BY s.surname, s.name
        """, (teacher_id,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def create_achievement(student_id, title, type_, level,
                       place, date, result, points=0):
    """
    Добавить достижение студенту.

    Args:
        student_id: id студента
        title: название
        type_: тип (Олимпиада, Выставка, Соревнование)
        level: уровень (Городской, Областной, Региональный)
        place: место (1, 2, 3)
        date: дата (ГГГГ-ММ-ДД)
        result: результат («1 место», «Участник»)
        points: баллы портфолио

    Returns:
        bool: True если успешно
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO achievement
            (student_id, title, type, level, place, date, result, points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, title, type_, level, place, date, result, points))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка создания достижения: {e}")
        return False
    finally:
        conn.close()


def delete_achievement(achievement_id):
    """Удалить достижение."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM achievement WHERE id = ?", (achievement_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_teacher_students_achievements_full(teacher_id):
    """
    Достижения студентов преподавателя — с id (для удаления).

    Returns:
        list[dict]: id, student_fio, title, type, level, date, result
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.id,
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
            ORDER BY a.date DESC
        """, (teacher_id,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()