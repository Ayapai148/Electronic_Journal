import hashlib
from db.database import get_connection


def get_users_count():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM users")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_students_count():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM students")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_teachers_count():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM teachers")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_clubs_count():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM clubs")
        row = cursor.fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_all_users():
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


def delete_user(user_id, user_login="", admin=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

        if admin:
            log_action(
                user_id=admin.get("id"),
                user_login=admin.get("login", "—"),
                action="Удалён пользователь",
                details=user_login
            )
        return cursor.rowcount > 0
    finally:
        conn.close()


def create_user(login, password, role):
    conn = get_connection()
    try:
        cursor = conn.cursor()

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


def get_clubs_report(period=None, club_id=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        where_parts = []
        params = []

        if club_id:
            where_parts.append("c.id = ?")
            params.append(club_id)

        if period:
            where_parts.append("l.date LIKE ?")
            params.append(f"{period}%")

        where_sql = ""
        if where_parts:
            where_sql = "WHERE " + " AND ".join(where_parts)

        query = f"""
            SELECT
                c.id,
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
            {where_sql}
            GROUP BY c.id
            ORDER BY c.name
        """

        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_report_periods():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT substr(date, 1, 7) AS period
            FROM lessons
            WHERE date IS NOT NULL
            ORDER BY period DESC
        """)
        rows = cursor.fetchall()

        month_names = {
            "01": "Январь", "02": "Февраль", "03": "Март",
            "04": "Апрель", "05": "Май", "06": "Июнь",
            "07": "Июль", "08": "Август", "09": "Сентябрь",
            "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь",
        }

        result = []
        for row in rows:
            period = row["period"]
            if not period:
                continue
            year, month = period.split("-")
            label = f"{month_names.get(month, month)} {year}"
            result.append({"value": period, "label": label})

        return result
    finally:
        conn.close()


def get_all_clubs_for_filter():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name
            FROM clubs
            ORDER BY name
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def get_recent_actions(limit=5):
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


def log_action(user_id, user_login, action, details=""):
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
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        if cursor.fetchone():
            return False

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
            (login, password_hash, role)
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

        if admin:
            role_ru = {
                "student": "студент",
                "teacher": "преподаватель",
                "admin": "администратор",
            }.get(role, role)

            log_action(
                user_id=admin.get("id"),
                user_login=admin.get("login", "—"),
                action="Добавлен пользователь",
                details=f"{fio} ({role_ru})"
            )

        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()


def get_all_clubs():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                c.id,
                c.name,
                c.type,
                c.schedule,
                c.room,
                c.teacher_id,
                COALESCE(
                    t.surname || ' ' || t.name,
                    '—'
                ) AS teacher_fio
            FROM clubs c
            LEFT JOIN teachers t ON c.teacher_id = t.id
            ORDER BY c.name
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def get_all_teachers_for_select():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                id,
                surname || ' ' || name AS fio
            FROM teachers
            ORDER BY surname
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()


def create_club(name, type_, teacher_id, schedule, room, admin=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO clubs (name, type, teacher_id, schedule, room)
               VALUES (?, ?, ?, ?, ?)""",
            (name, type_, teacher_id, schedule, room)
        )
        conn.commit()

        if admin:
            log_action(
                user_id=admin.get("id"),
                user_login=admin.get("login", "—"),
                action="Добавлен кружок",
                details=f"{name} ({type_})"
            )
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()


def update_club(club_id, name, type_, teacher_id, schedule, room, admin=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE clubs
               SET name = ?, type = ?, teacher_id = ?, schedule = ?, room = ?
               WHERE id = ?""",
            (name, type_, teacher_id, schedule, room, club_id)
        )
        conn.commit()

        if admin:
            log_action(
                user_id=admin.get("id"),
                user_login=admin.get("login", "—"),
                action="Изменён кружок",
                details=f"{name}"
            )
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        return False
    finally:
        conn.close()


def delete_club(club_id, club_name="", admin=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clubs WHERE id = ?", (club_id,))
        conn.commit()

        if admin:
            log_action(
                user_id=admin.get("id"),
                user_login=admin.get("login", "—"),
                action="Удалён кружок",
                details=club_name
            )
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_backups_dir():
    from pathlib import Path

    base = Path(__file__).parent.parent
    backups = base / "backups"
    backups.mkdir(exist_ok=True)
    return backups


def backup_db():
    import shutil
    from datetime import datetime
    from pathlib import Path

    base = Path(__file__).parent.parent
    src = base / "ejksr.db"

    if not src.exists():
        return None

    backups = get_backups_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = backups / f"ejksr_{timestamp}.db"

    try:
        shutil.copy(src, dst)
        return str(dst)
    except Exception as e:
        print(f"Ошибка создания резервной копии: {e}")
        return None


def get_backups_list():
    from pathlib import Path

    backups = get_backups_dir()
    files = sorted(backups.glob("ejksr_*.db"), reverse=True)

    result = []
    for f in files:
        stat = f.stat()
        result.append({
            "filename": f.name,
            "path": str(f),
            "size_kb": round(stat.st_size / 1024, 1),
        })
    return result


def restore_db(filename):
    import shutil
    from pathlib import Path

    backups = get_backups_dir()
    src = backups / filename

    if not src.exists():
        return False

    base = Path(__file__).parent.parent
    dst = base / "ejksr.db"

    try:
        shutil.copy(src, dst)
        return True
    except Exception as e:
        print(f"Ошибка восстановления: {e}")
        return False

def get_backups_dir():
    from pathlib import Path

    base = Path(__file__).parent.parent
    backups = base / "backups"
    backups.mkdir(exist_ok=True)
    return backups


def backup_db():
    import shutil
    from datetime import datetime
    from pathlib import Path

    base = Path(__file__).parent.parent
    src = base / "ejksr.db"

    if not src.exists():
        return None

    backups = get_backups_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = backups / f"ejksr_{timestamp}.db"

    try:
        shutil.copy(src, dst)
        return str(dst)
    except Exception as e:
        print(f"Ошибка создания резервной копии: {e}")
        return None


def get_backups_list():
    from pathlib import Path

    backups = get_backups_dir()
    files = sorted(backups.glob("ejksr_*.db"), reverse=True)

    result = []
    for f in files:
        stat = f.stat()
        result.append({
            "filename": f.name,
            "path": str(f),
            "size_kb": round(stat.st_size / 1024, 1),
        })
    return result


def restore_db(filename):
    import shutil
    from pathlib import Path

    backups = get_backups_dir()
    src = backups / filename

    if not src.exists():
        return False

    base = Path(__file__).parent.parent
    dst = base / "ejksr.db"

    try:
        shutil.copy(src, dst)
        return True
    except Exception as e:
        print(f"Ошибка восстановления: {e}")
        return False