import sqlite3
from pathlib import Path
import datetime

DB_PATH = Path("data/db/data.db")

CHUNK_SIZE = 1000
OVERLAP = 150


def get_transcripts_not_chunked(cur):
    cur.execute("""
        SELECT t.video_id, t.transcript
        FROM transcripts t
        LEFT JOIN transcript_chunks c 
        ON t.video_id = c.video_id
        WHERE c.video_id IS NULL
    """)
    return cur.fetchall()


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def run():
    print("🚀 Starting Chunking Process...")

    if not DB_PATH.exists():
        print("❌ Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    transcripts = get_transcripts_not_chunked(cur)

    print(f"📊 Transcripts to chunk: {len(transcripts)}")

    total_chunks = 0

    for video_id, transcript in transcripts:
        print(f"🔍 Chunking video: {video_id}")

        chunks = chunk_text(transcript)

        for idx, chunk in enumerate(chunks):
            cur.execute("""
                INSERT INTO transcript_chunks
                (video_id, chunk_index, chunk_text, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                video_id,
                idx,
                chunk,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

        total_chunks += len(chunks)

    conn.commit()
    conn.close()

    print(f"✅ Total chunks created: {total_chunks}")


if __name__ == "__main__":
    run()
