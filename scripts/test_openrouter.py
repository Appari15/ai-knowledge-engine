import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config.settings import get_settings

settings = get_settings()

# Try multiple free models until one works
models_to_try = [
    "google/gemma-3-12b-it:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-4b:free",
    "google/gemma-3-4b-it:free",
]

print("Testing FREE models to find one that works...\n")

for model in models_to_try:
    print(f"Trying: {model}...")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": "Say hello in 5 words"}],
            "max_tokens": 30,
        },
        timeout=30,
    )

    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        print(f"  ✅ WORKS! Response: {answer}")
        print(f"\n{'='*50}")
        print(f"USE THIS MODEL: {model}")
        print(f"{'='*50}")
        print(f"\nRun this command:")
        print(f'  notepad .env')
        print(f"  Change OPENROUTER_MODEL to: {model}")
        break
    else:
        error = response.json().get("error", {}).get("message", "Unknown error")
        print(f"  ❌ Failed: {error[:80]}")

else:
    print("\nAll models rate-limited. Wait 5 minutes and try again.")