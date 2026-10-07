from db.database import get_connection


def get_student_by_user_id(user_id):
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


def get_clubs_count(student_id):
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


def get_average_grade(student_id):
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


def get_attendance_rate(student_id):
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


def get_achievements_count(student_id):
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


def get_upcoming_lessons(student_id, limit=5):
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


def get_schedule(student_id):
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
            parts = sched.split(",")
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                tokens = part.split()
                if len(tokens) < 2:
                    continue
                day_short = tokens[0]
                time_str = tokens[1] if len(tokens) > 1 else ""

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


def get_grades(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT
                   l.date,
                   l.topic,
                   a.grade,
                   a.comment,
                   a.status,
                   c.name AS club_name,
                   t.surname || ' ' || t.name AS teacher_fio
               FROM attendance a
               JOIN lessons l ON a.lesson_id = l.id
               JOIN clubs c ON l.club_id = c.id
               JOIN teachers t ON c.teacher_id = t.id
               WHERE a.student_id = ?
               ORDER BY c.name, l.date DESC""",
            (student_id,)
        )
        rows = [dict(r) for r in cursor.fetchall()]

        # Считаем посещаемость по каждому кружку
        club_stats = {}
        for r in rows:
            club = r["club_name"]
            if club not in club_stats:
                club_stats[club] = {"total": 0, "present": 0}
            club_stats[club]["total"] += 1
            if r["status"] != "НБ":
                club_stats[club]["present"] += 1

        # Прикрепляем посещаемость к каждой записи
        for r in rows:
            club = r["club_name"]
            stats = club_stats[club]
            if stats["total"] > 0:
                r["attendance"] = round(stats["present"] * 100 / stats["total"])
            else:
                r["attendance"] = 0

        return rows
    finally:
        conn.close()


def get_teachers_list():
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


def get_groupmates(group):
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


def get_achievements(student_id):
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


def get_student_lessons_filtered(student_id, period="month"):
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
                c.room,
                t.surname || ' ' || t.name AS teacher_fio
            FROM lessons l
            JOIN clubs c ON l.club_id = c.id
            JOIN teachers t ON c.teacher_id = t.id
            WHERE c.id IN (
                SELECT club_id FROM enrollments
                WHERE student_id = ? AND status = 'active'
            )
            AND l.date BETWEEN ? AND ?
            ORDER BY l.date, c.name
        """, (student_id, date_from, date_to))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()