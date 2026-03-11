from typing import List
from .config import client, EMBED_MODEL, EMBED_DIM

def embed_text(text: str) -> List[float]:
    res = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config={"output_dimensionality": EMBED_DIM},
    )
    return res.embeddings[0].values