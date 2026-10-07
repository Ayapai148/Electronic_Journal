import pytest
from logic.auth import (
    hash_password, authenticate,
    register_student, register_teacher,
    find_user_by_email, generate_reset_code,
    save_reset_code, verify_reset_code,
    update_password, mark_code_used,
)


def test_hash_password():
    h1 = hash_password("12345")
    h2 = hash_password("12345")
    assert h1 == h2
    assert len(h1) == 64


def test_hash_password_different():
    h1 = hash_password("12345")
    h2 = hash_password("54321")
    assert h1 != h2


def test_register_student():
    result = register_student(
        fio="Петров Пётр",
        login="petrov",
        password="123456",
        group="ИСП-34",
        email="petrov@test.ru"
    )
    assert result is True


def test_register_teacher():
    result = register_teacher(
        fio="Иванов Иван",
        login="ivanov",
        password="123456",
        direction="Информатика",
        email="ivanov@test.ru"
    )
    assert result is True


def test_register_duplicate_login():
    register_student("Петров Пётр", "petrov", "123456", "ИСП-34")
    result = register_student("Другой Студент", "petrov", "54321", "ИСП-35")
    assert result is False


def test_authenticate_success():
    register_student("Петров Пётр", "petrov", "123456", "ИСП-34")
    user = authenticate("petrov", "123456")
    assert user is not None
    assert user["login"] == "petrov"
    assert user["role"] == "student"


def test_authenticate_wrong_password():
    register_student("Петров Пётр", "petrov", "123456", "ИСП-34")
    user = authenticate("petrov", "wrong")
    assert user is None


def test_authenticate_wrong_login():
    user = authenticate("no_such_user", "123456")
    assert user is None


def test_find_user_by_email():
    register_student("Петров Пётр", "petrov", "123456",
                     "ИСП-34", "petrov@test.ru")
    user = find_user_by_email("petrov@test.ru")
    assert user is not None
    assert user["login"] == "petrov"


def test_find_user_by_email_not_found():
    user = find_user_by_email("no_such@test.ru")
    assert user is None


def test_generate_reset_code():
    code = generate_reset_code()
    assert len(code) == 6
    assert code.isdigit()


def test_save_and_verify_code():
    register_student("Петров Пётр", "petrov", "123456",
                     "ИСП-34", "petrov@test.ru")
    user = find_user_by_email("petrov@test.ru")

    save_reset_code(user["id"], "petrov@test.ru", "123456")
    reset = verify_reset_code("petrov@test.ru", "123456")

    assert reset is not None
    assert reset["user_id"] == user["id"]


def test_verify_wrong_code():
    register_student("Петров Пётр", "petrov", "123456",
                     "ИСП-34", "petrov@test.ru")
    user = find_user_by_email("petrov@test.ru")

    save_reset_code(user["id"], "petrov@test.ru", "111111")
    reset = verify_reset_code("petrov@test.ru", "999999")

    assert reset is None


def test_update_password():
    register_student("Петров Пётр", "petrov", "123456",
                     "ИСП-34", "petrov@test.ru")
    user = find_user_by_email("petrov@test.ru")

    update_password(user["id"], "newpass")

    assert authenticate("petrov", "newpass") is not None
    assert authenticate("petrov", "123456") is None


def test_mark_code_used():
    register_student("Петров Пётр", "petrov", "123456",
                     "ИСП-34", "petrov@test.ru")
    user = find_user_by_email("petrov@test.ru")

    save_reset_code(user["id"], "petrov@test.ru", "123456")
    reset = verify_reset_code("petrov@test.ru", "123456")

    mark_code_used(reset["id"])

    assert verify_reset_code("petrov@test.ru", "123456") is None