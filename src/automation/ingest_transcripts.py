
import sqlite3
import time
import random
import datetime
from pathlib import Path

from src.phase1.fetch_transcript import fetch_transcript_chunks

DB_PATH = Path("data/db/data.db")


def get_videos_missing_transcripts(cur):
    """Return video_ids that do not yet have transcripts."""
    cur.execute("""
        SELECT v.video_id
        FROM videos v
        LEFT JOIN transcripts t ON v.video_id = t.video_id
        WHERE t.video_id IS NULL
    """)
    return [row[0] for row in cur.fetchall()]


def insert_transcript_as_block(cur, video_id, chunks):
    """Combine chunks and insert full transcript as single text block."""
    full_text = " ".join([chunk["text"] for chunk in chunks])
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO transcripts (video_id, transcript, language, fetched_at)
        VALUES (?, ?, ?, ?)
    """, (
        video_id,
        full_text,
        "te",
        now
    ))

    # Mark video as processed
    cur.execute("""
        UPDATE videos
        SET processed = 1
        WHERE video_id = ?
    """, (video_id,))


def log_error(cur, video_id, message):
    """Optional: simple error logging (prints only)."""
    print(f"[ERROR LOG] {video_id} → {message}")


def run():
    print("🚀 Starting Transcript Ingestion (Full Text Mode)...")

    if not DB_PATH.exists():
        print(f"❌ Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    missing_videos = get_videos_missing_transcripts(cur)
    print(f"📊 Total videos to process: {len(missing_videos)}")

    success = 0
    failed = 0

    for video_id in missing_videos:
        print(f"🔍 Fetching: {video_id}...")

        try:
            # Fetch transcript chunks
            chunks = fetch_transcript_chunks(video_id)

            # Insert transcript and update processed flag
            insert_transcript_as_block(cur, video_id, chunks)

            conn.commit()
            success += 1
            print(f"✅ Saved full transcript for: {video_id}")

        except Exception as e:
            clean_error = str(e).split('\n')[0]
            print(f"❌ Failed: {video_id} | Error: {clean_error}")
            log_error(cur, video_id, clean_error)
            conn.commit()
            failed += 1

        # Sleep to avoid rate limits
        pause = random.uniform(10, 20)
        print(f"💤 Sleeping for {int(pause)}s...")
        time.sleep(pause)

    conn.close()

    print("\n" + "=" * 40)
    print(f"🏁 DONE! Successfully stored: {success}, Failed: {failed}")
    print("=" * 40)


if __name__ == "__main__":
    run()
