from db.database import get_connection


def get_teacher_by_user_id(user_id):
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


def get_teacher_clubs(teacher_id):
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


def get_teacher_students_count(teacher_id):
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


def get_lessons_by_club(club_id):
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


def get_teacher_attendance_rate(teacher_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   COUNT(*) AS total,
                   SUM(CASE WHEN a.status != 'НБ' THEN 1 ELSE 0 END) AS present
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


def get_teacher_students_achievements(teacher_id):
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


def get_teacher_students_achievements_full(teacher_id):
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


def get_teacher_schedule(teacher_id):
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


def get_teacher_clubs_full(teacher_id):
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
    conn = get_connection()
    try:
        cursor = conn.cursor()

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
    #Удалить кружок вместе со связанными занятиями и записями
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверяем, что кружок принадлежит этому преподавателю
        cursor.execute(
            "SELECT id FROM clubs WHERE id = ? AND teacher_id = ?",
            (club_id, teacher_id)
        )
        if not cursor.fetchone():
            return False

        # Удаляем посещаемость занятий этого кружка
        cursor.execute("""
            DELETE FROM attendance
            WHERE lesson_id IN (
                SELECT id FROM lessons WHERE club_id = ?
            )
        """, (club_id,))

        # Удаляем занятия
        cursor.execute("DELETE FROM lessons WHERE club_id = ?", (club_id,))

        # Удаляем записи студентов
        cursor.execute("DELETE FROM enrollments WHERE club_id = ?", (club_id,))

        # Удаляем сам кружок
        cursor.execute("DELETE FROM clubs WHERE id = ?", (club_id,))

        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Ошибка удаления кружка: {e}")
        return False
    finally:
        conn.close()


def get_all_students():
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


def get_students_by_club(club_id):
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


def update_grade(lesson_id, student_id, grade, comment=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        if grade is None:
            status = "НБ"
        else:
            status = "Присутствовал"

        cursor.execute("""
            SELECT id FROM attendance
            WHERE lesson_id = ? AND student_id = ?
        """, (lesson_id, student_id))

        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE attendance
                SET grade = ?, comment = ?, status = ?
                WHERE id = ?
            """, (grade, comment, status, row["id"]))
        else:
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


def create_lesson(club_id, date, topic, type_="Практика", hours=2, group=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lessons (date, topic, type, hours, club_id)
            VALUES (?, ?, ?, ?, ?)
        """, (date, topic, type_, hours, club_id))

        lesson_id = cursor.lastrowid
        conn.commit()

        if group:
            add_group_to_lesson(lesson_id, group, club_id)

        return lesson_id
    except Exception as e:
        conn.rollback()
        print(f"Ошибка создания занятия: {e}")
        return None
    finally:
        conn.close()


def get_student_averages(club_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                a.student_id,
                AVG(a.grade) AS avg_grade,
                COUNT(a.id) AS total_records,
                SUM(CASE WHEN a.grade IS NOT NULL THEN 1 ELSE 0 END) AS present_count
            FROM attendance a
            JOIN lessons l ON a.lesson_id = l.id
            WHERE l.club_id = ?
            GROUP BY a.student_id
        """, (club_id,))

        result = {}
        for row in cursor.fetchall():
            avg = row["avg_grade"] or 0
            total = row["total_records"] or 0
            present = row["present_count"] or 0

            attendance = 0
            if total > 0:
                attendance = round(present * 100 / total)

            result[row["student_id"]] = {
                "avg": round(avg, 2),
                "final": round(avg),
                "attendance": attendance,
            }
        return result
    finally:
        conn.close()


def create_achievement(student_id, title, type_, level,
                       place, date, result, points=0):
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
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM achievement WHERE id = ?", (achievement_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_teacher_lessons_filtered(teacher_id, period="month"):
    from datetime import date, timedelta

    today = date.today()

    if period == "today":
        date_from = today.isoformat()
        date_to = today.isoformat()
    elif period == "week":
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        date_from = monday.isoformat()
        date_to = sunday.isoformat()
    elif period == "month":
        first = today.replace(day=1)
        if today.month == 12:
            last = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        date_from = first.isoformat()
        date_to = last.isoformat()
    else:
        date_from = "1900-01-01"
        date_to = "2100-01-01"

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                l.date,
                l.topic,
                l.type,
                l.hours,
                c.name AS club_name,
                c.room
            FROM lessons l
            JOIN clubs c ON l.club_id = c.id
            WHERE c.teacher_id = ?
              AND l.date BETWEEN ? AND ?
            ORDER BY l.date, c.name
        """, (teacher_id, date_from, date_to))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_all_groups():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT groups
            FROM students
            WHERE groups IS NOT NULL AND groups != ''
            ORDER BY groups
        """)
        return [row["groups"] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_students_by_group(group, club_id=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        if club_id:
            cursor.execute("""
                SELECT DISTINCT
                    s.id,
                    s.surname || ' ' || s.name AS fio,
                    s.groups
                FROM students s
                JOIN enrollments e ON e.student_id = s.id
                WHERE s.groups = ? AND e.club_id = ? AND e.status = 'active'
                ORDER BY s.surname, s.name
            """, (group, club_id))
        else:
            cursor.execute("""
                SELECT
                    id,
                    surname || ' ' || name AS fio,
                    groups
                FROM students
                WHERE groups = ?
                ORDER BY surname, name
            """, (group,))

        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def add_group_to_lesson(lesson_id, group, club_id=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        students = get_students_by_group(group, club_id)

        added = 0
        for s in students:
            cursor.execute("""
                SELECT id FROM attendance
                WHERE lesson_id = ? AND student_id = ?
            """, (lesson_id, s["id"]))

            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT INTO attendance
                (lesson_id, student_id, status, cause, grade, comment)
                VALUES (?, ?, '', '', NULL, '')
            """, (lesson_id, s["id"]))
            added += 1

        conn.commit()
        return added
    except Exception as e:
        conn.rollback()
        print(f"Ошибка добавления группы: {e}")
        return 0
    finally:
        conn.close()


def enroll_group_to_club(club_id, group):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        students = get_students_by_group(group, club_id=None)

        added = 0
        for s in students:
            cursor.execute("""
                SELECT id FROM enrollments
                WHERE club_id = ? AND student_id = ?
            """, (club_id, s["id"]))

            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT INTO enrollments
                (student_id, club_id, enroll_date, status)
                VALUES (?, ?, date('now'), 'active')
            """, (s["id"], club_id))
            added += 1

        conn.commit()
        return added
    except Exception as e:
        conn.rollback()
        print(f"Ошибка записи группы: {e}")
        return 0
    finally:
        conn.close()
def get_teacher_students(teacher_id):
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