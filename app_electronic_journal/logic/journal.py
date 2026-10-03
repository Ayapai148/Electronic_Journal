from db.database import get_connection

def students_by_group(group: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE groups = ? ORDER BY surname",
            (group,)
        )
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def add_attendance(lesson_id, student_id, status, cause=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO attendance (lesson_id, student_id, status, cause)
                VALUES (?, ?, ?, ?)""",
            (lesson_id, student_id, status, cause)
        )
        conn.commit()
        return True
    finally:
        conn.close()