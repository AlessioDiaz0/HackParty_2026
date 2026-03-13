import json
import os
import requests

# We'll use environment variables or hardcoded defaults for simplicity in this bridge
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
LLM_MODEL = "meta/llama-3.1-8b-instruct"

# Load API key from env or root file
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "").strip()
if not NVIDIA_API_KEY:
    _key_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "api_keys.txt")
    if os.path.exists(_key_file):
        with open(_key_file) as f:
            NVIDIA_API_KEY = f.read().strip()

DOMAIN_CATEGORIES = [
    "Task", "Bug", "Enhancement", "Research", "Design", "Testing", "Deployment", "Documentation"
]

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
    def __init__(self, categories=None):
        self._categories = categories or DOMAIN_CATEGORIES
        self._system_prompt = SYSTEM_PROMPT.format(
            categories="\n".join(f"- {c}" for c in self._categories)
        )

    def classify(self, message):
        if not NVIDIA_API_KEY:
            return {"category": "Task", "confidence": "high", "reasoning": "API Key missing, dummy response."}
            
        try:
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
                "max_tokens": 256
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

            result = json.loads(raw)
        except Exception as e:
            print(f"Error in classification: {e}")
            result = {
                "category": "Task",
                "confidence": "low",
                "reasoning": f"Error processing LLM response: {str(e)}",
            }

        if result.get("category") not in self._categories:
            result["category"] = "Task"
            result["confidence"] = "low"

        return result
