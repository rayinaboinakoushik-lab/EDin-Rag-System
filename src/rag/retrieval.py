from typing import Dict, List
import psycopg2
from pgvector.psycopg2 import register_vector
from .config import PG_HOST, PG_DB, PG_USER, PG_PASSWORD, SIMILARITY_THRESHOLD

def retrieve_top_k(query_vector: List[float], k: int = 5) -> List[Dict]:
    """
    Retrieve top-k docs with similarity score.
    similarity = 1 - cosine_distance
    Returns list of dict: {id, content, similarity}
    """
    conn = psycopg2.connect(
        host=PG_HOST,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    register_vector(conn)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, content, (1 - (embedding <=> %s::vector)) AS similarity
        FROM documents
        ORDER BY similarity DESC
        LIMIT %s
        """,
        (query_vector, k)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"id": row[0], "content": row[1], "similarity": float(row[2])}
        for row in rows
    ]

def apply_threshold(results: List[Dict]) -> List[Dict]:
    """Keep only results with similarity >= threshold."""
    return [r for r in results if r["similarity"] >= SIMILARITY_THRESHOLD]

def mean_similarity(results: List[Dict]) -> float:
    """Average similarity used as confidence."""
    if not results:
        return 0.0
    return round(sum(r["similarity"] for r in results) / len(results), 2)