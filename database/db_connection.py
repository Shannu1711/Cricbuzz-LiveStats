from pathlib import Path
import sqlite3


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_FOLDER / "data" / "cricbuzz.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


if __name__ == "__main__":
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' ORDER BY name"
        ).fetchall()

    table_names = [row["name"] for row in rows]
    print("Connected to the database.")
    print("Tables:", ", ".join(table_names))