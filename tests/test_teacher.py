from logic.auth import register_teacher
from logic.teacher import (
    get_teacher_by_user_id, get_teacher_clubs,
    create_teacher_club, update_teacher_club,
    delete_teacher_club,
)


def _create_teacher():
    register_teacher(
        fio="Иванов Иван Иванович",
        login="ivanov",
        password="123456",
        direction="Информатика",
        email="ivanov@test.ru"
    )
    from db.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id FROM teachers")
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def test_get_teacher_by_user_id():
    data = _create_teacher()
    teacher = get_teacher_by_user_id(data["user_id"])
    assert teacher is not None
    assert teacher["surname"] == "Иванов"


def test_get_teacher_clubs_empty():
    data = _create_teacher()
    teacher = get_teacher_by_user_id(data["user_id"])
    clubs = get_teacher_clubs(teacher["id"])
    assert clubs == []


def test_create_teacher_club():
    data = _create_teacher()
    teacher = get_teacher_by_user_id(data["user_id"])

    result = create_teacher_club(
        teacher["id"], "Робототехника", "Кружок",
        "Пн 15:00-16:30", "204"
    )
    assert result is True

    clubs = get_teacher_clubs(teacher["id"])
    assert len(clubs) == 1
    assert clubs[0]["name"] == "Робототехника"


def test_update_teacher_club():
    data = _create_teacher()
    teacher = get_teacher_by_user_id(data["user_id"])

    create_teacher_club(teacher["id"], "Робототехника",
                        "Кружок", "Пн 15:00-16:30", "204")

    clubs = get_teacher_clubs(teacher["id"])
    club_id = clubs[0]["id"]

    result = update_teacher_club(
        club_id, teacher["id"], "Робототехника+",
        "Кружок", "Пн 16:00-17:30", "205"
    )
    assert result is True

    clubs = get_teacher_clubs(teacher["id"])
    assert clubs[0]["name"] == "Робототехника+"
    assert clubs[0]["room"] == "205"


def test_delete_teacher_club():
    data = _create_teacher()
    teacher = get_teacher_by_user_id(data["user_id"])

    create_teacher_club(teacher["id"], "Робототехника",
                        "Кружок", "Пн 15:00-16:30", "204")

    clubs = get_teacher_clubs(teacher["id"])
    club_id = clubs[0]["id"]

    result = delete_teacher_club(club_id, teacher["id"])
    assert result is True

    clubs = get_teacher_clubs(teacher["id"])
    assert clubs == []