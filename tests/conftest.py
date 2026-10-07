import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def use_test_db():
    test_db = Path(__file__).parent.parent / "test_ejksr.db"

    if test_db.exists():
        test_db.unlink()

    original_path = Path(__file__).parent.parent / "db" / "database.py"

    import db.database as database_module
    database_module.DB_PATH = test_db

    from db.database import init_db
    init_db()

    yield test_db

    if test_db.exists():
        test_db.unlink()


@pytest.fixture(autouse=True)
def clean_tables():
    from db.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    tables = [
        "password_reset", "audit_log", "enrollments",
        "attendance", "achievement", "portfolio_student",
        "lessons", "clubs", "students", "teachers", "users",
    ]

    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except Exception:
            pass

    conn.commit()
    conn.close()

    yield