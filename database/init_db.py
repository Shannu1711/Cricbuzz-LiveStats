from pathlib import Path
import sqlite3


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_FOLDER / "data" / "cricbuzz.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def create_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema)

    print(f"Database created at: {DATABASE_PATH}")


if __name__ == "__main__":
    create_database()