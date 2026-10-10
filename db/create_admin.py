from database import get_connection
import hashlib

LOGIN = "admin"
PASSWORD = "admin123"


def create_admin():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE login = ?", (LOGIN,))
        if cursor.fetchone():
            print(f"Админ {LOGIN} уже существует")
            return

        password_hash = hashlib.sha256(PASSWORD.encode()).hexdigest()

        cursor.execute(
            "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
            (LOGIN, password_hash, "admin")
        )
        conn.commit()
        print("Администратор создан")
        print(f"Логин: {LOGIN}")
        print(f"Пароль: {PASSWORD}")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_admin()