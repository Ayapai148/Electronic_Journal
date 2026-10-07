from logic.auth import register_student
from logic.student import (
    get_student_by_user_id, get_clubs_count,
    get_average_grade, get_attendance_rate,
    get_achievements_count, get_student_lessons_filtered,
)


def _create_student():
    register_student(
        fio="Петров Пётр Петрович",
        login="petrov",
        password="123456",
        group="ИСП-34",
        email="petrov@test.ru"
    )
    from db.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id FROM students WHERE groups = 'ИСП-34'")
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def test_get_student_by_user_id():
    data = _create_student()
    student = get_student_by_user_id(data["user_id"])
    assert student is not None
    assert student["surname"] == "Петров"


def test_get_clubs_count_empty():
    data = _create_student()
    student = get_student_by_user_id(data["user_id"])
    count = get_clubs_count(student["id"])
    assert count == 0


def test_get_average_grade_no_grades():
    data = _create_student()
    student = get_student_by_user_id(data["user_id"])
    avg = get_average_grade(student["id"])
    assert avg is None


def test_get_attendance_rate_empty():
    data = _create_student()
    student = get_student_by_user_id(data["user_id"])
    rate = get_attendance_rate(student["id"])
    assert rate is None


def test_get_achievements_count_empty():
    data = _create_student()
    student = get_student_by_user_id(data["user_id"])
    count = get_achievements_count(student["id"])
    assert count == 0


def test_get_student_lessons_filtered_empty():
    data = _create_student()
    student = get_student_by_user_id(data["user_id"])
    lessons = get_student_lessons_filtered(student["id"], "all")
    assert lessons == []