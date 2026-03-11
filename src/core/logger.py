import json
import os
from datetime import datetime

# This will create a 'logs' folder in your main EDin directory
LOG_FILE = "logs/rag_logs.jsonl"

def log_request(question, similarities, doc_ids, confidence):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "top_similarity": max(similarities) if similarities else 0,
        "mean_similarity": round(sum(similarities)/len(similarities), 3) if similarities else 0,
        "documents_used": doc_ids,
        "confidence": confidence
    }

    # Safety: Create the 'logs' folder if it's missing
    os.makedirs("logs", exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")