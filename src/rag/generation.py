import json
from typing import Dict
from .config import client, GEN_MODEL, SYSTEM_PROMPT

def _extract_json_object(text: str) -> str:
    """
    Brutal JSON extractor:
    - strips code fences
    - extracts substring from first '{' to last '}'
    """
    if not text:
        return ""

    t = text.strip()
    t = t.replace("```json", "").replace("```", "").strip()

    start = t.find("{")
    end = t.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return ""

    return t[start:end+1]

def generate_answer(context_text: str, user_query: str) -> Dict:
    """
    Calls Gemini in strict mode and returns parsed JSON dict.
    Does NOT set sources/confidence — app.py injects those.
    """
    user_prompt = (
        f"CONTEXT:\n{context_text}\n\n"
        f"QUESTION: {user_query}\n\n"
        "Return ONLY valid JSON. No markdown. No extra text."
    )

    response = client.models.generate_content(
        model=GEN_MODEL,
        contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        
    )

    raw = getattr(response, "text", "") or ""
    json_text = _extract_json_object(raw)

    if not json_text:
        return {"answer": "Invalid model output", "sources": [], "confidence": 0.0}

    try:
        parsed = json.loads(json_text)
        # Ensure expected keys exist
        if "answer" not in parsed:
            parsed["answer"] = "Invalid model output"
        if "sources" not in parsed:
            parsed["sources"] = []
        if "confidence" not in parsed:
            parsed["confidence"] = 0.0
        return parsed
    except Exception:
        return {"answer": "Invalid model output", "sources": [], "confidence": 0.0}