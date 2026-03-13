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

OUTCOMES_DIR = os.path.join(os.path.dirname(__file__), "generated_outcomes")


def save_outcome(message: str, result: dict, doc_id: str) -> str:
    """Save a classification outcome as a JSON file and return the path."""
    os.makedirs(OUTCOMES_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}.json"
    filepath = os.path.join(OUTCOMES_DIR, filename)

    outcome = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "category": result["category"],
        "confidence": result["confidence"],
    }

    with open(filepath, "w") as f:
        json.dump(outcome, f, indent=2)

    return filepath


def print_header():
    print("=" * 60)
    print("  Customer Message Zero-Shot Classifier")
    print("  NVIDIA NIM  |  ChromaDB Vector Store")
    print("=" * 60)


def print_result(message: str, result: dict):
    print(f"\n{'─' * 50}")
    print(f"  Message:    {message}")
    print(f"  Category:   {result['category']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"{'─' * 50}")


def run_interactive():
    """Interactive mode: user types messages, system classifies them."""
    classifier = ZeroShotClassifier()
    store = EmbeddingStore()

    print("\nType a customer message (or 'quit' to exit, 'stats' for stats,")
    print("'search:<query>' to find similar messages):\n")

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

        # Classify and store
        result = classifier.classify(user_input)
        doc_id = store.add_message(
            user_input, result["category"], result["confidence"]
        )
        path = save_outcome(user_input, result, doc_id)
        print_result(user_input, result)
        print(f"  Saved to: {path}")


def main():
    print_header()
    run_interactive()


if __name__ == "__main__":
    main()
