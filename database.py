import sqlite3

DATABASE_NAME = "students.db"


def get_connection(db_name: str = None):
    name = db_name if db_name else DATABASE_NAME
    connection = sqlite3.connect(name)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_table(db_name: str = None):
    with get_connection(db_name) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT    NOT NULL,
                date_of_birth   TEXT    NOT NULL,
                email           TEXT,
                phone           TEXT,
                course          TEXT    NOT NULL,
                address         TEXT,
                enrollment_date TEXT    NOT NULL
            )
        """)
