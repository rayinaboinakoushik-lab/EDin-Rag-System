import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "db" / "data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    result = None
    if fetch:
        result = cursor.fetchall()

    conn.commit()
    conn.close()
    return result
