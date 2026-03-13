"""
Zero-shot customer message classifier using NVIDIA NIM.

Classifies customer messages into domain categories using only
prompt engineering — no pre-provided examples.
"""

import json
import requests

from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, LLM_MODEL, DOMAIN_CATEGORIES


SYSTEM_PROMPT = """\
You are an expert customer-service message classifier.

Your task: given a customer message, classify it into EXACTLY ONE of the
following domain categories:

{categories}

Rules:
1. Choose the single best-matching category from the list above.
2. Do NOT invent new categories.
3. Assess your confidence as "high", "medium", or "low".
4. Respond ONLY with valid JSON — no extra text, no markdown fences.

Required JSON format:
{{"category": "<chosen category>", "confidence": "<high|medium|low>", "reasoning": "<one-sentence explanation>"}}
"""


class ZeroShotClassifier:
    """Classifies customer messages into domain categories via prompt engineering."""

    def __init__(self, categories: list[str] | None = None):
        self._categories = categories or DOMAIN_CATEGORIES
        self._system_prompt = SYSTEM_PROMPT.format(
            categories="\n".join(f"- {c}" for c in self._categories)
        )

    def classify(self, message: str) -> dict:
        """
        Classify a single customer message.

        Returns dict with keys: category, confidence, reasoning.
        """
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": 0.0,
            "max_tokens": 256,
        }
        
        response = requests.post(f"{NVIDIA_BASE_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        raw = data['choices'][0]['message']['content'].strip()

        # Strip possible markdown code fences
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {
                "category": "Task",
                "confidence": "low",
                "reasoning": f"Failed to parse model response: {raw[:200]}",
            }

        # Validate category
        if result.get("category") not in self._categories:
            result["category"] = "Task"
            result["confidence"] = "low"

        return result

    def classify_batch(self, messages: list[str]) -> list[dict]:
        """Classify multiple messages."""
        return [self.classify(m) for m in messages]
