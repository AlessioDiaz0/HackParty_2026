#!/usr/bin/env python3
"""
Customer Message Zero-Shot Classifier — NVIDIA NIM + ChromaDB

Classifies incoming customer messages into domain categories using
zero-shot prompt engineering (no pre-provided examples).
Stores classified messages as embeddings in ChromaDB for similarity search.
"""

import json
import os
from datetime import datetime

from classifier import ZeroShotClassifier
from embeddings import EmbeddingStore
from translator import LaraTranslator, LANGUAGES

OUTCOMES_DIR = os.path.join(os.path.dirname(__file__), "generated_outcomes")


def save_outcome(original: str, message: str, result: dict, doc_id: str,
                 source_lang: str = "", target_lang: str = "") -> str:
    """Save a classification outcome as a JSON file and return the path."""
    os.makedirs(OUTCOMES_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}.json"
    filepath = os.path.join(OUTCOMES_DIR, filename)

    outcome = {
        "timestamp": datetime.now().isoformat(),
        "original": original,
        "translation": message,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "category": result["category"],
        "confidence": result["confidence"],
        "urgency": result.get("urgency", "Medium"),
    }

    with open(filepath, "w") as f:
        json.dump(outcome, f, indent=2)

    return filepath


def print_header():
    print("=" * 60)
    print("  Customer Message Zero-Shot Classifier")
    print("  NVIDIA NIM  |  ChromaDB Vector Store")
    print("=" * 60)


def print_result(original: str, translated: str, result: dict, source_lang: str):
    urgency = result.get("urgency", "Medium")
    print(f"\n{'─' * 50}")
    print(f"  Original:    {original}")
    if original != translated:
        print(f"  Translated:  {translated}  (from {source_lang})")
    print(f"  Category:    {result['category']}")
    print(f"  Confidence:  {result['confidence']}")
    print(f"  Urgency:     {urgency}")
    print(f"{'─' * 50}")


def run_interactive():
    """Interactive mode: user types messages, system classifies them."""
    classifier = ZeroShotClassifier()
    store = EmbeddingStore()
    lara = LaraTranslator(target_lang="en")

    print(f"\nTranslation target: English (en)")
    print("Commands:")
    print("  lang:<code>   — change translation language (e.g. lang:es, lang:fr)")
    print("  languages     — list available language codes")
    print("  search:<query> — find similar messages")
    print("  stats         — show category stats")
    print("  quit          — exit\n")

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "languages":
            print("  Available language codes:")
            for code, full in sorted(LANGUAGES.items()):
                print(f"    {code}  →  {full}")
            continue
        if user_input.lower().startswith("lang:"):
            code = user_input[5:].strip().lower()
            if code not in LANGUAGES:
                print(f"  Unknown code '{code}'. Type 'languages' to see options.")
                continue
            lara.set_target(code)
            print(f"  Translation target set to: {LANGUAGES[code]} ({code})")
            continue
        if user_input.lower() == "stats":
            stats = store.get_stats()
            print(f"  Total: {stats['total_messages']}")
            for cat, count in sorted(stats["categories"].items()):
                print(f"    {cat}: {count}")
            continue
        if user_input.lower().startswith("search:"):
            query = user_input[7:].strip()
            if not query:
                print("  Provide a search query after 'search:'")
                continue
            results = store.query_similar(query, n_results=3)
            if results["documents"] and results["documents"][0]:
                for i, (doc, meta) in enumerate(
                    zip(
                        results["documents"][0],
                        results["metadatas"][0],
                    )
                ):
                    print(f"  {i + 1}. [{meta['category']}] {doc}")
            else:
                print("  No stored messages yet.")
            continue

        # Translate, classify and store
        tr = lara.translate(user_input)
        translated = tr["translated"]
        source_lang = tr["source_lang"]

        result = classifier.classify(translated)
        doc_id = store.add_message(
            translated, result["category"], result["confidence"],
            urgency=result.get("urgency", "Medium"),
        )

        # Reorder display by urgency
        urgency_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        urgency = result.get("urgency", "Medium")
        if urgency == "Critical":
            print("\n  ⚠  CRITICAL URGENCY — immediate attention required!")

        path = save_outcome(
            user_input, translated, result, doc_id,
            source_lang=source_lang, target_lang=lara.target_code,
        )
        print_result(user_input, translated, result, source_lang)
        print(f"  Saved to: {path}")


def main():
    print_header()
    run_interactive()


if __name__ == "__main__":
    main()
