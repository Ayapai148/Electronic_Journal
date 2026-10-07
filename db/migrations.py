from database import get_connection


def add_grade_to_attendance():
    conn = get_connection()
    try:
        cursor = conn.cursor()
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


def migrate_statuses():
    """
    Миграция статусов:
    - Отсутствовал → НБ
    - Опоздал → Присутствовал
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE attendance
            SET status = 'НБ'
            WHERE status = 'Отсутствовал'
        """)
        count_nb = cursor.rowcount

        cursor.execute("""
            UPDATE attendance
            SET status = 'Присутствовал'
            WHERE status = 'Опоздал'
        """)
        count_late = cursor.rowcount

        conn.commit()
        print(f"Отсутствовал → НБ: {count_nb} записей")
        print(f"Опоздал → Присутствовал: {count_late} записей")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка миграции статусов: {e}")
    finally:
        conn.close()


def run_migrations():
    print("Запуск миграций...")
    add_grade_to_attendance()
    add_comment_to_attendance()
    migrate_statuses()
    print("Миграции завершены.")


if __name__ == "__main__":
    run_migrations()