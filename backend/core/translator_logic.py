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

SYSTEM_PROMPT = """\
You are an expert translator and localization assistant.

Your task: given a JSON object containing UI strings in a source language, translate ALL values into the target language specified by the user.

Rules:
1. Preserve all JSON keys exactly as they are.
2. Translate only the values.
3. Maintain the style, tone, and any special characters (like emojis or placeholders) in the translations.
4. Respond ONLY with the translated JSON — no extra text, no markdown fences.
5. If you cannot translate a specific string, leave it in the source language.

Target Language: {target_lang}
"""

class Translator:
    def __init__(self):
        pass

    def translate(self, source_dict: dict, target_lang: str) -> dict:
        if not NVIDIA_API_KEY:
            # Fallback dummy if no API key
            return {k: f"[{target_lang}] {v}" for k, v in source_dict.items()}
            
        try:
            headers = {
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            system_prompt = SYSTEM_PROMPT.format(target_lang=target_lang)
            
            payload = {
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(source_dict, ensure_ascii=False)},
                ],
                "temperature": 0.1,
                "max_tokens": 4096
            }
            
            response = requests.post(f"{NVIDIA_BASE_URL}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            raw = data['choices'][0]['message']['content'].strip()
            
            # Strip possible markdown code fences
            if raw.startswith("```"):
                # Handle cases like ```json ... ``` or just ``` ... ```
                lines = raw.split("\n")
                if lines[0].startswith("```"):
                    raw = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])
                raw = raw.strip()

            result = json.loads(raw)
            return result
        except Exception as e:
            print(f"Error in translation: {e}")
            # Fallback to source
            return source_dict
