import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# import your Phase 1 metadata fetcher
from phase1.fetch_metadata import fetch_video_metadata  

DB_PATH = Path("data/db/data.db")

def get_existing_video_ids(cursor):
    cursor.execute("SELECT video_id FROM videos")
    return {row[0] for row in cursor.fetchall()}

def detect_and_store_new_videos(channel_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    existing_ids = get_existing_video_ids(cursor)

    videos = fetch_video_metadata(channel_id)

    new_count = 0

    for video in videos:
        if video["video_id"] not in existing_ids:
            cursor.execute("""
                INSERT INTO videos (video_id, title, published_at)
                VALUES (?, ?, ?)
            """, (
                video["video_id"],
                video["title"],
                video["published_at"]
            ))
            new_count += 1

    conn.commit()
    conn.close()

    print(f"New videos detected: {new_count}")

if __name__ == "__main__":
    detect_and_store_new_videos("UCmeSC2WkskoLgOV5aVGlRrg")
