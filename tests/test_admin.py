from logic.auth import register_student
from logic.admin import (
    get_users_count, get_students_count,
    get_teachers_count, get_clubs_count,
    get_all_users, create_user_with_profile,
    backup_db, get_backups_list,
)


def test_get_users_count_empty():
    assert get_users_count() == 0


def test_create_user_student():
    result = create_user_with_profile(
        fio="Сидоров Сидор",
        login="sidorov",
        password="123456",
        role="student",
        group="ИСП-35"
    )
    assert result is True
    assert get_users_count() == 1
    assert get_students_count() == 1


def test_create_user_teacher():
    result = create_user_with_profile(
        fio="Иванов Иван",
        login="ivanov",
        password="123456",
        role="teacher",
        direction="Информатика"
    )
    assert result is True
    assert get_users_count() == 1
    assert get_teachers_count() == 1


def test_create_duplicate_user():
    create_user_with_profile(
        "Сидоров Сидор", "sidorov", "123456",
        "student", group="ИСП-35"
    )
    result = create_user_with_profile(
        "Другой", "sidorov", "123456",
        "student", group="ИСП-36"
    )
    assert result is False


def test_get_all_users():
    create_user_with_profile(
        "Сидоров Сидор", "sidorov", "123456",
        "student", group="ИСП-35"
    )
    users = get_all_users()
    assert len(users) == 1
    assert users[0]["login"] == "sidorov"


def test_get_clubs_count_empty():
    assert get_clubs_count() == 0


def test_backup_db():
    register_student("Тест", "test", "123456", "ИСП-34")
    path = backup_db()
    assert path is not None

    backups = get_backups_list()
    assert len(backups) >= 1