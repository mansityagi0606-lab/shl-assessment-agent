import json
import os
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# =========================
# PATHS
# =========================

DATA_PATH = "data/processed/shl_catalog_cleaned.json"

FAISS_DIR = "data/faiss"

INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")

METADATA_PATH = os.path.join(FAISS_DIR, "metadata.pkl")

# =========================
# LOAD EMBEDDING MODEL
# =========================

print("\nLoading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded.\n")


def load_catalog():

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def generate_embeddings(texts):

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    return embeddings


def build_faiss_index(embeddings):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def main():

    # =========================
    # LOAD DATA
    # =========================

    print("Loading cleaned catalog...")

    catalog = load_catalog()

    print(f"Loaded {len(catalog)} assessments.\n")

    # =========================
    # PREPARE SEARCH TEXTS
    # =========================

    search_texts = []

    metadata = []

    for item in catalog:

        search_texts.append(
            item["search_text"]
        )

        metadata.append({
            "name": item["name"],
            "url": item["url"],
            "category": item["category"],
            "skills": item["skills"],
            "description": item["description"],
            "test_type": item["test_type"]
        })

    # =========================
    # GENERATE EMBEDDINGS
    # =========================

    print("Generating embeddings...\n")

    embeddings = generate_embeddings(
        search_texts
    )

    print(f"\nEmbeddings shape: {embeddings.shape}")

    # =========================
    # BUILD FAISS INDEX
    # =========================

    print("\nBuilding FAISS index...")

    index = build_faiss_index(
        embeddings
    )

    print("FAISS index created.")

    # =========================
    # CREATE DIRECTORY
    # =========================

    os.makedirs(FAISS_DIR, exist_ok=True)

    # =========================
    # SAVE INDEX
    # =========================

    faiss.write_index(
        index,
        INDEX_PATH
    )

    # =========================
    # SAVE METADATA
    # =========================

    with open(METADATA_PATH, "wb") as f:

        pickle.dump(metadata, f)

    # =========================
    # FINAL LOGS
    # =========================

    print("\n========== FAISS BUILD COMPLETE ==========")

    print(f"Index saved to:\n{INDEX_PATH}")

    print(f"\nMetadata saved to:\n{METADATA_PATH}")

    print(f"\nTotal vectors indexed: {index.ntotal}")


if __name__ == "__main__":
    main()