import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# --- ENV / CONSTANTS ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

PG_HOST = os.getenv("PGHOST", "postgres")
PG_DB = os.getenv("PGDATABASE", "rag_db")
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("PGPASSWORD")  # never hardcode secrets

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.67"))

EMBED_MODEL = "models/gemini-embedding-001"
EMBED_DIM = 3072
GEN_MODEL = "gemini-2.5-flash-lite"

if not GOOGLE_API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY. Put it in your .env file.")
if not PG_PASSWORD:
    raise RuntimeError("Missing PGPASSWORD. Put it in your .env file.")

# ✅ Fix 2: shared client (importable everywhere)
client = genai.Client(api_key=GOOGLE_API_KEY)

# ✅ Fix 1: SYSTEM_PROMPT must be a named variable
SYSTEM_PROMPT = """
You are a NEET advisory assistant.

You must follow these rules strictly:

1. Use ONLY the provided context.
2. If the answer is not explicitly present in the context, return exactly:
{
  "answer": "Not found in available data.",
  "sources": [],
  "confidence": 0.0
}

3. Do NOT use external knowledge.
4. Do NOT guess.
5. Output strictly valid JSON.
6. No extra explanations.
"""