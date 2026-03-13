import requests
import json

def test_backend():
    print("Testing base-translations...")
    try:
        r = requests.get('http://localhost:8000/api/base-translations')
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Keys found: {len(data)}")
            if 'header_title' in data:
                print("✓ Base translations OK")
            else:
                print("✗ Missing keys in translations")
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\nTesting translate (placeholder)...")
    try:
        payload = {
            "source_strings": {"test": "prova"},
            "target_lang": "en"
        }
        r = requests.post('http://localhost:8000/api/translate', json=payload)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Response: {data.get('message')}")
            print("✓ Translate placeholder OK")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_backend()
