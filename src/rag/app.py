from src.core.logger import log_request
from .embeddings import embed_text
from .retrieval import retrieve_top_k, apply_threshold, mean_similarity
from .generation import generate_answer
from .config import SIMILARITY_THRESHOLD

def ask_edin(user_query: str) -> dict:
    """
    Core RAG pipeline for the EDin project.
    Handles embedding, pgvector retrieval, and generation with safety guards.
    """
    # Initialize variables to ensure they exist for the logger even if an error occurs
    similarities = []
    doc_ids = []
    confidence = 0.0
    final_result = {}

    try:
        
        # 1. Embedding: Convert query to vector
        query_vector = embed_text(user_query)

        # 2. Retrieval: Search pgvector for the top 5 relevant chunks
        results = retrieve_top_k(query_vector, k=5)
        filtered = apply_threshold(results)

        # Extract metadata for tracking and confidence scoring
        similarities = [r["similarity"] for r in filtered]
        doc_ids = [r["id"] for r in filtered]

        if not filtered:
            confidence = 0.0
        else:
            confidence = mean_similarity(filtered)

        # 3. Gating: Check against SIMILARITY_THRESHOLD to prevent hallucinations
        if not filtered or confidence < SIMILARITY_THRESHOLD:
            final_result = {
                "answer": "Not found in available data.",
                "sources": [],
                "confidence": 0.0
            }
        else:
            # Combine retrieved content into a single context string
            context_text = "\n\n".join(r["content"] for r in filtered)

            # 4. Generation: Request answer from the GenAI model
            final_result = generate_answer(context_text, user_query)

            # Type check to ensure the external generation module returned a valid dict
            if not isinstance(final_result, dict):
                raise Exception("Invalid generation output")

            # Append retrieval metadata to the successful result
            final_result["sources"] = doc_ids
            final_result["confidence"] = confidence

    except Exception as e:
        # Catch issues like youtubeapi errors or missing dotenv variables
        print(f"⚠️ INTERNAL ERROR: {e}")

        final_result = {
            "answer": "The AI service is currently overwhelmed or unavailable. Please try again in a moment.",
            "sources": [],
            "confidence": 0.0
        }

    # 5. Logging: Persistent record of the interaction (Proof of Work)
    try:
        log_request(user_query, similarities, doc_ids, confidence)
    except Exception as log_error:
        print(f"⚠️ LOGGING ERROR: {log_error}")

    return final_result
if __name__ == "__main__":
    # This keeps the script running in your terminal for testing
    print("--- EDIN RAG SYSTEM ACTIVE ---")
    while True:
        user_input = input("\nAsk Question: ")
        if user_input.lower() == 'exit':
            break
        
        response = ask_edin(user_input)
        print(f"\nResponse: {response['answer']}")
        print(f"Confidence: {response['confidence']}")