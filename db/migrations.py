
from database import get_connection


def add_grade_to_attendance():
    """
    Добавить колонку grade в таблицу attendance.
    Если колонка уже есть — ничего не делает.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Проверяем, есть ли колонка grade
        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row["name"] for row in cursor.fetchall()]

        if "grade" in columns:
            print("Колонка grade уже существует в attendance")
            return

        cursor.execute("ALTER TABLE attendance ADD COLUMN grade INTEGER")
        conn.commit()
        print("Колонка grade добавлена в attendance")
    except Exception as e:
        print(f"Ошибка миграции: {e}")
    finally:
        conn.close()


def add_comment_to_attendance():
    """
    Добавить колонку comment в таблицу attendance.
    Для примечаний к оценке.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row["name"] for row in cursor.fetchall()]

        if "comment" in columns:
            print("Колонка comment уже существует в attendance")
            return

        cursor.execute("ALTER TABLE attendance ADD COLUMN comment TEXT")
        conn.commit()
        print("Колонка comment добавлена в attendance")
    except Exception as e:
        print(f"Ошибка миграции: {e}")
    finally:
        conn.close()


def run_migrations():
    """Запустить все миграции."""
    print("Запуск миграций...")
    add_grade_to_attendance()
    add_comment_to_attendance()
    print("Миграции завершены.")


if __name__ == "__main__":
    run_migrations()