# ============================================================
# PHASE 2 – CLEANING + TOKENIZATION + STOPWORDS + TF-IDF
# (FINAL VERSION – NO LEMMATIZATION)
# ============================================================

import json
import re
from pathlib import Path
from collections import Counter
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------- PATHS ----------
DATASET_PATH = Path("../data/combined_dataset.json")

CLEAN_TEXT_PATH = Path("clean_text.json")
SENT_TOKENS_PATH = Path("sentence_tokens.json")
WORD_TOKENS_PATH = Path("word_tokens.json")
STOPWORD_WORD_TOKENS_PATH = Path("clean_word_tokens.json")
TFIDF_CLEAN_PATH = Path("tfidf_clean_keywords.json")
CLEAN_TEXT_PATH = Path("clean_text.json")
NER_OUTPUT_PATH = Path("named_entities.json")
SENTENCE_TOKENS_PATH = Path("sentence_tokens.json")
TFIDF_KEYWORDS_PATH = Path("tfidf_clean_keywords.json")
SUMMARY_OUTPUT_PATH = Path("extractive_summary.json")


# ============================================================
# STEP 1 — CLEANING
# ============================================================

def load_combined_text():
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["combined_text"]


def clean_text(text: str) -> str:
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def step1_cleaning():
    raw = load_combined_text()

    cleaned = clean_text(raw)

    with CLEAN_TEXT_PATH.open("w", encoding="utf-8") as f:
        json.dump({"cleaned_text": cleaned}, f, ensure_ascii=False, indent=2)

    print("Step-1 CLEANING DONE →", CLEAN_TEXT_PATH)


# ============================================================
# STEP 2 — SENTENCE TOKENIZATION (10 WORD CHUNKS)
# ============================================================

def size_based_sentence_tokenize(text: str, chunk_size=10):
    words = text.split()
    sentences = []

    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        if len(chunk) < 3:
            break
        sentences.append(" ".join(chunk))

    return sentences


def step2_sentence_tokens():
    with CLEAN_TEXT_PATH.open("r", encoding="utf-8") as f:
        cleaned = json.load(f)["cleaned_text"]

    sentences = size_based_sentence_tokenize(cleaned, chunk_size=10)

    with SENT_TOKENS_PATH.open("w", encoding="utf-8") as f:
        json.dump({"sentence_tokens": sentences}, f, ensure_ascii=False, indent=2)

    print("Step-2 SENTENCE TOKENS DONE →", SENT_TOKENS_PATH)


# ============================================================
# STEP 3 — WORD TOKENIZATION
# ============================================================

def word_tokenize(text: str):
    return [t for t in text.split(" ") if t.strip()]


def step3_word_tokens():
    with CLEAN_TEXT_PATH.open("r", encoding="utf-8") as f:
        cleaned = json.load(f)["cleaned_text"]

    tokens = word_tokenize(cleaned)

    with WORD_TOKENS_PATH.open("w", encoding="utf-8") as f:
        json.dump({"word_tokens": tokens}, f, ensure_ascii=False, indent=2)

    print("Step-3 WORD TOKENS DONE →", WORD_TOKENS_PATH)


# ============================================================
# STEP 4 — STOPWORD REMOVAL
# ============================================================

TELUGU_STOPWORDS = {
    "అండ్", "ది", "గా", "అయితే", "సో", "లో", "కాని", "మీరు",
    "అంటే", "ఇప్పుడు", "కూడా", "మన", "అవి", "వీళ్ళు"
}

def remove_stopwords(tokens):
    return [t for t in tokens if t not in TELUGU_STOPWORDS]


def step4_stopword_cleaning():
    with WORD_TOKENS_PATH.open("r", encoding="utf-8") as f:
        tokens = json.load(f)["word_tokens"]

    cleaned = remove_stopwords(tokens)

    with STOPWORD_WORD_TOKENS_PATH.open("w", encoding="utf-8") as f:
        json.dump({"clean_word_tokens": cleaned}, f, ensure_ascii=False, indent=2)

    print("Step-4 STOPWORD CLEANING DONE →", STOPWORD_WORD_TOKENS_PATH)


# ============================================================
# STEP 5 — REMOVED (NO LEMMATIZATION)
# ============================================================



# ============================================================
# STEP 6 — TF-IDF KEYWORD EXTRACTION
# ============================================================

def compute_tfidf(words, top_k=30):
    # Join the cleaned word list back into a string
    text = " ".join(words)

    vectorizer = TfidfVectorizer(
        tokenizer=lambda x: x.split(),     # use our own tokens
        preprocessor=lambda x: x,          # do not modify
        token_pattern=None,                # disable sklearn regex
        lowercase=False                     # avoid ASCII lowercasing
    )

    tfidf_matrix = vectorizer.fit_transform([text])
    scores = tfidf_matrix.toarray()[0]
    vocab = vectorizer.get_feature_names_out()

    ranked = list(zip(vocab, scores))
    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:top_k] 



def step6_tfidf():
    with STOPWORD_WORD_TOKENS_PATH.open("r", encoding="utf-8") as f:
        words = json.load(f)["clean_word_tokens"]

    keywords = compute_tfidf(words, top_k=50)

    with TFIDF_CLEAN_PATH.open("w", encoding="utf-8") as f:
        json.dump({"tfidf_clean_keywords": keywords}, f, ensure_ascii=False, indent=2)

    print("Step-6 TF-IDF DONE →", TFIDF_CLEAN_PATH)

# ============================================================
# STEP-7 — RULE-BASED NER (TELUGU)
# ============================================================

# ============================================================
# STEP 7 — RULE-BASED NER (TELUGU)
# ============================================================




# ============================================================
# LOAD CLEANED TEXT
# ============================================================

def load_cleaned_text():
    with CLEAN_TEXT_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cleaned_text"]


# ============================================================
# NER EXTRACTION LOGIC
# ============================================================

def extract_entities(text: str):
    entities = {
        "marks": [],
        "seats": [],
        "categories": [],
        "rounds": [],
        "college_type": []
    }

    # ---------- MARKS (NUMBERS LIKE 371, 402, 415) ----------
    entities["marks"] = list(
        set(re.findall(r"\b[3-4][0-9]{2}\b", text))
    )

    # ---------- SEATS (NUMBERS FOLLOWED BY సీట్స్ / మెంబర్స్) ----------
    entities["seats"] = list(
        set(re.findall(r"\b\d+\s?(?:సీట్స్|సీట్|మెంబర్స్)\b", text))
    )

    # ---------- CATEGORIES ----------
    category_patterns = [
        "ఓపెన్", "ఎస్టీ", "ఎస్సి", "ఎస్సి3", "ఎస్సి టూ",
        "బిసిఏ", "బిసిఈ", "బిసిడి", "బిసిసి", "బిసిబి"
    ]

    for cat in category_patterns:
        if cat in text:
            entities["categories"].append(cat)

    # ---------- ROUNDS ----------
    round_patterns = ["ఫస్ట్", "సెకండ్", "థర్డ్"]
    for r in round_patterns:
        if r in text:
            entities["rounds"].append(r)

    # ---------- COLLEGE TYPE ----------
    if "గవర్నమెంట్" in text:
        entities["college_type"].append("గవర్నమెంట్")
    if "ప్రైవేట్" in text:
        entities["college_type"].append("ప్రైవేట్")

    return entities


# ============================================================
# RUN STEP 7
# ============================================================

def run_step7_ner():
    print("\n🚀 Step-7: Running Rule-Based NER...\n")

    text = load_cleaned_text()
    ner_entities = extract_entities(text)

    # Print preview
    for key, values in ner_entities.items():
        print(f"{key.upper()} → {values}")

    # Save output
    with NER_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(ner_entities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Step-7 Complete → {NER_OUTPUT_PATH}\n")

# ============================================================
# STEP 8 — EXTRACTIVE SUMMARIZATION (PHASE-2 FINAL)
# ============================================================



# ============================================================
# UTILITY: LOAD JSON FILE
# ============================================================

def load_json(file_path: Path):
    """Load JSON file safely."""
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# CORE LOGIC: EXTRACTIVE SUMMARY
# ============================================================

def extractive_summary(sentences, tfidf_keywords, top_n=7):
    """
    Generate extractive summary by scoring sentences
    using TF-IDF keyword weights.
    """

    # Convert TF-IDF list -> dictionary for fast lookup
    tfidf_dict = {word: score for word, score in tfidf_keywords}

    # Sentence index -> cumulative score
    sentence_scores = defaultdict(float)

    # Score each sentence
    for idx, sentence in enumerate(sentences):
        words = sentence.split()

        for word in words:
            if word in tfidf_dict:
                sentence_scores[idx] += tfidf_dict[word]

    # Rank sentences by score (descending)
    ranked = sorted(
        sentence_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Select top-N sentence indices
    top_sentence_indices = sorted(
        [idx for idx, _ in ranked[:top_n]]
    )

    # Preserve original order
    summary_sentences = [sentences[idx] for idx in top_sentence_indices]

    return summary_sentences


# ============================================================
# RUN STEP-8
# ============================================================

def run_step8_summarization():
    print("\n🚀 Step-8: Running Extractive Summarization...\n")

    # Load inputs
    sentences = load_json(SENTENCE_TOKENS_PATH)["sentence_tokens"]
    tfidf_data = load_json(TFIDF_KEYWORDS_PATH)["tfidf_clean_keywords"]

    # Generate summary
    summary = extractive_summary(sentences, tfidf_data, top_n=7)

    # Save output
    with SUMMARY_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            {"extractive_summary": summary},
            f,
            ensure_ascii=False,
            indent=2
        )

    # Print summary for validation
    print("=== EXTRACTIVE SUMMARY ===")
    for s in summary:
        print("-", s)

    print(f"\n✅ Step-8 complete → {SUMMARY_OUTPUT_PATH}\n")


# ============================================================
# MAIN ENTRY POINT
# ============================================================


# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n🚀 Running PHASE-2 Pipeline (Final, Safe Version)...\n")

    step1_cleaning()
    step2_sentence_tokens()
    step3_word_tokens()
    step4_stopword_cleaning()
    step6_tfidf()
    run_step7_ner()
    run_step8_summarization()
    print("\n🎉 PHASE-2 COMPLETED SUCCESSFULLY!\n")
