import os
import requests
import json

_key_file = os.path.join(os.getcwd(), "api_keys.txt")
with open(_key_file) as f:
    key = f.read().strip()

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [
        {"role": "user", "content": "Ciao, rispondi con 'OK' se mi senti."}
    ],
    "temperature": 0.0,
    "max_tokens": 10
}

url = "https://integrate.api.nvidia.com/v1/chat/completions"

print(f"Testing URL: {url}")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
