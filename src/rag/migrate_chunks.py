import os
import time
import sqlite3
import psycopg2
from dotenv import load_dotenv
from google import genai
from pgvector.psycopg2 import register_vector

# ---------- CONFIGURATION ----------
load_dotenv()

# SQLite DB inside container
SQLITE_PATH = "/app/edin.db"

# PostgreSQL configuration
PG_CONFIG = {
    "host": os.getenv("PGHOST", "postgres"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "rag_db"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),
}

# Gemini configuration
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "models/gemini-embedding-001"


def migrate():

    print("🚀 Starting High-Fidelity Migration (3072-dim)...")

    # ---------- STEP 1: Verify SQLite file ----------
    if not os.path.exists(SQLITE_PATH):
        print(f"❌ SQLite file not found: {SQLITE_PATH}")
        return

    # ---------- STEP 2: Fetch chunks ----------
    try:
        print("using sqlite DB:", SQLITE_PATH)
        conn = sqlite3.connect(SQLITE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, chunk_text FROM transcript_chunks")
        chunks = cursor.fetchall()

        conn.close()

        print(f"📦 Found {len(chunks)} chunks in SQLite")

    except Exception as e:
        print(f"❌ SQLite Error: {e}")
        return


    # ---------- STEP 3: Connect to Postgres ----------
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        # Set autocommit to True so extension creation isn't trapped in a transaction
        pg_conn.autocommit = True 
        
        pg_cur = pg_conn.cursor()

        # 1️⃣ FIRST: Enable the extension in the DB
        pg_cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ pgvector extension enabled")

        # 2️⃣ SECOND: Register the type so Python/psycopg2 understands it
        register_vector(pg_conn)

        # 3️⃣ THIRD: Create your table
        pg_cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            source TEXT UNIQUE,
            content TEXT,
            embedding vector(3072)
        );
        """)

        print("✅ Postgres Table Verified with 3072-dim support")

    except Exception as e:
        print(f"❌ Postgres Setup Error: {e}")
        return


    # ---------- STEP 4: Gemini client ----------
    client = genai.Client(api_key=API_KEY)

    success_count = 0


    # ---------- STEP 5: Process chunks ----------
    for cid, text in chunks:

        try:
            # Generate 3072-dim embedding
            res = client.models.embed_content(
                model=MODEL_NAME,
                contents=text,
                config={"output_dimensionality": 3072},
            )

            vector = res.embeddings[0].values

            # Insert with Upsert logic
            pg_cur.execute(
                """
                INSERT INTO documents (source, content, embedding)
                VALUES (%s, %s, %s)
                ON CONFLICT (source) DO UPDATE
                SET content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding;
                """,
                (str(cid), text, vector),
            )

            success_count += 1

            if success_count % 5 == 0:
                print(f"✅ Progress: {success_count}/{len(chunks)}")

            # Standard rate-limit safety sleep
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error at chunk {cid}: {e}")
            if "429" in str(e):
                print("⏳ Rate limit hit. Sleeping 30s...")
                time.sleep(30)


    pg_cur.close()
    pg_conn.close()

    print(f"✨ Migration Complete! {success_count} chunks stored.")


if __name__ == "__main__":
    migrate()