# preprocess/phase2_nlp_pipeline.py
# Phase 2 – FINAL VERSION (V8 + Step 4)
# Clean → Remove Dots → 10-Word Sentence Tokenization → Word Tokenization → Stopword Removal

import json




import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------- FILE PATHS ----------
DATASET_PATH = Path("../data/combined_dataset.json")

OUTPUT_CLEAN_TEXT = Path("combined_text.json")
OUTPUT_SENTENCE_TOKENS = Path("sentence_tokens.json")
OUTPUT_WORD_TOKENS = Path("word_tokens.json")
OUTPUT_CLEAN_SENTENCE_TOKENS = Path("cleaned_sentence_tokens.json")
CLEAN_WORDS_PATH = Path("cleaned_word_tokens.json")
TFIDF_KEYWORDS_PATH = Path("tfidf_clean_keywords.json")




# ---------- STOPWORDS (Hybrid Strategy C) ----------

# General Telugu + conversational filler words
TELUGU_STOPWORDS = [
    "అండి", "అంటే", "అయితే", "అప్పుడు", "అలా", "ఇలా", "ఇక్కడ", "ఇంకా",
    "కూడా", "మరి", "మాత్రమే", "అండ్", "సో", "ఒక", "ది", "లో", "కి", "పై",
    "తో", "గాను", "వంటి", "గా", "కోసం", "ఎందుకంటే", "చాలా", "వీళ్ళు",
    "వీళ్ళకి", "ఈ", "ఆ", "అది", "ఇది", "ఉంటుంది", "ఉన్నాయి", "ఉందా",
    "ఉంది", "వరకు", "చెప్పొచ్చు", "చూద్దాం", "అదే", "మాత్రం"
]

# NEET-domain important words we NEVER remove
DOMAIN_WORDS = [
    "నీట్", "యూజి", "యుజి",
    "ర్యాంక్", "ర్యాంక్స్", "ర్యాంకులు",
    "కటాఫ్", "కటాఫ్స్",
    "మార్క్", "మార్కులు", "మార్క్స్",
    "సీట్లు", "సీట్", "సీట్స్",
    "కాలేజ్", "కాలేజీ", "కాలేజీలు", "కాలేజెస్",
    "అలాట్మెంట్", "అలాట్మెంట్స్",
    "కేటగిరీ", "కేటగిరీలు",
    "ప్రైవేట్", "గవర్నమెంట్",
    "థర్డ్", "సెకండ్", "ఫస్ట్",
    "రౌండ్", "రౌండ్స్",
    "మెరిట్", "స్టేట్", "ఆల్", "ఇండియా"
]


# ============================================================
# STEP 1 — CLEANING (WITH DOT REMOVAL)
# ============================================================

def load_combined_text():
    """Load raw combined_text from dataset JSON."""
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["combined_text"]


def clean_text(text: str) -> str:
    """Clean text: remove dots + collapse whitespace."""
    text = text.replace(".", " ")       # REMOVE ALL DOTS
    text = re.sub(r"\s+", " ", text)    # collapse whitespace
    text = text.strip()
    return text


def step1_cleaning():
    raw_text = load_combined_text()

    print("\n=== RAW TEXT (FIRST 300 CHARS) ===")
    print(raw_text[:300])

    cleaned = clean_text(raw_text)

    print("\n=== CLEANED TEXT (FIRST 300 CHARS) ===")
    print(cleaned[:300], "\n")

    with OUTPUT_CLEAN_TEXT.open("w", encoding="utf-8") as f:
        json.dump({"cleaned_text": cleaned}, f, ensure_ascii=False, indent=2)

    print(f"Step 1 ✅ Cleaning complete → {OUTPUT_CLEAN_TEXT}")


# ============================================================
# STEP 2 — SIZE-BASED SENTENCE TOKENIZATION (10 WORDS EACH)
# ============================================================

def size_based_sentence_tokenize(text: str, chunk_size=10):
    """Split text into exact 10-word chunks."""
    words = text.split()
    sentences = []

    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]

        if len(chunk) < 3:  # ignore tiny leftovers
            break

        sentence = " ".join(chunk)
        sentences.append(sentence)

    return sentences


def step2_sentence_tokenization():
    with OUTPUT_CLEAN_TEXT.open("r", encoding="utf-8") as f:
        cleaned = json.load(f)["cleaned_text"]

    sentences = size_based_sentence_tokenize(cleaned, chunk_size=10)

    print("\n=== FIRST 10 SENTENCES ===")
    for s in sentences[:10]:
        print("-", s)

    with OUTPUT_SENTENCE_TOKENS.open("w", encoding="utf-8") as f:
        json.dump({"sentence_tokens": sentences}, f, ensure_ascii=False, indent=2)

    print(f"Step 2 ✅ Sentence tokens saved → {OUTPUT_SENTENCE_TOKENS}")


# ============================================================
# STEP 3 — WORD TOKENIZATION
# ============================================================

def word_tokenize(text: str):
    tokens = text.split()
    return tokens


def step3_word_tokenization():
    with OUTPUT_CLEAN_TEXT.open("r", encoding="utf-8") as f:
        cleaned = json.load(f)["cleaned_text"]

    tokens = word_tokenize(cleaned)

    print("\n=== FIRST 20 WORD TOKENS ===")
    print(tokens[:20])

    with OUTPUT_WORD_TOKENS.open("w", encoding="utf-8") as f:
        json.dump({"word_tokens": tokens}, f, ensure_ascii=False, indent=2)

    print(f"Step 3 ✅ Word tokens saved → {OUTPUT_WORD_TOKENS}")


# ============================================================
# STEP 4 — STOPWORD REMOVAL (ON WORDS + SENTENCES)
# ============================================================

def remove_stopwords_from_tokens(tokens, stopwords):
    """Remove Telugu stopwords while keeping NEET domain words."""
    cleaned = []
    for t in tokens:
        t_stripped = t.strip()
        if not t_stripped:
            continue

        # Always keep domain-important words
        if t_stripped in DOMAIN_WORDS:
            cleaned.append(t_stripped)
            continue

        # Skip stopwords
        if t_stripped in stopwords:
            continue

        cleaned.append(t_stripped)

    return cleaned


def remove_stopwords_from_sentences(sentences, stopwords):
    """
    Remove stopwords inside each sentence.
    Returns a list of cleaned sentences.
    """
    cleaned_sentences = []

    for s in sentences:
        words = s.split()
        cleaned_words = remove_stopwords_from_tokens(words, stopwords)

        # If everything got removed, skip sentence
        if not cleaned_words:
            continue

        cleaned_sentence = " ".join(cleaned_words)
        cleaned_sentences.append(cleaned_sentence)

    return cleaned_sentences


def step4_stopword_removal():
    # 1) Clean word tokens
    with OUTPUT_WORD_TOKENS.open("r", encoding="utf-8") as f:
        tokens = json.load(f)["word_tokens"]

    cleaned_word_tokens = remove_stopwords_from_tokens(tokens, TELUGU_STOPWORDS)

    print("\n=== CLEANED WORD TOKENS (FIRST 30) ===")
    print(cleaned_word_tokens[:30])

    with CLEAN_WORDS_PATH.open("w", encoding="utf-8") as f:
        json.dump({"cleaned_word_tokens": cleaned_word_tokens},
                  f, ensure_ascii=False, indent=2)

    print(f"Step 4a ✅ Cleaned word tokens saved → {CLEAN_WORDS_PATH}")

    # 2) Clean sentence tokens
    with OUTPUT_SENTENCE_TOKENS.open("r", encoding="utf-8") as f:
        sentences = json.load(f)["sentence_tokens"]

    cleaned_sentence_tokens = remove_stopwords_from_sentences(
        sentences, TELUGU_STOPWORDS
    )

    print("\n=== CLEANED SENTENCES (FIRST 5) ===")
    for s in cleaned_sentence_tokens[:5]:
        print("-", s)

    with OUTPUT_CLEAN_SENTENCE_TOKENS.open("w", encoding="utf-8") as f:
        json.dump({"cleaned_sentence_tokens": cleaned_sentence_tokens},
                  f, ensure_ascii=False, indent=2)

    print(f"Step 4b ✅ Cleaned sentence tokens saved → {OUTPUT_CLEAN_SENTENCE_TOKENS}") 
# ============================================================

def load_clean_tokens():
    """Load cleaned word tokens from JSON file."""
    with CLEAN_WORDS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # IMPORTANT: Exact key name as confirmed by you
    return data["cleaned_word_tokens"]


def compute_tfidf_keywords(words, top_k=30):
    """
    Compute TF-IDF scores for cleaned tokens.
    Words list -> Convert to one document -> TF-IDF -> Top K keywords.
    """

    # Join all tokens into one string (TF-IDF expects text input)
    document = " ".join(words)

    # Create vectorizer
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")

    # Fit-transform
    tfidf_matrix = vectorizer.fit_transform([document])

    # Extract features & scores
    scores = tfidf_matrix.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()

    # Pair words with their scores
    scored_words = list(zip(feature_names, scores))

    # Sort by highest score
    sorted_keywords = sorted(scored_words, key=lambda x: x[1], reverse=True)

    # Select top K
    return sorted_keywords[:top_k]


def run_step6_tfidf():
    print("\n🚀 Step-6: Running TF-IDF Keyword Extraction...\n")

    # Load tokens
    tokens = load_clean_tokens()

    # Compute TF-IDF
    top_keywords = compute_tfidf_keywords(tokens, top_k=40)

    # Preview top 10
    print("Top TF-IDF Keywords:")
    for word, score in top_keywords[:10]:
        print(f"  {word} → {score:.4f}")

    # Save results
    with TFIDF_KEYWORDS_PATH.open("w", encoding="utf-8") as f:
        json.dump({"tfidf_clean_keywords": top_keywords}, f, ensure_ascii=False, indent=2)

    print(f"\nStep-6 ✅ TF-IDF keywords saved → {TFIDF_KEYWORDS_PATH}\n")


# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n🚀 Running Phase 2 — CLEANING + TOKENIZATION + STOPWORDS...\n")

    step1_cleaning()
    step2_sentence_tokenization()
    step3_word_tokenization()
    step4_stopword_removal()
    run_step6_tfidf()
    print("\n🎉 ALL DONE: Phase-2 (Steps 1–5) complete successfully!\n")
