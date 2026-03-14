"""Find a FREE model that works RIGHT NOW."""
import requests
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config.settings import get_settings

settings = get_settings()

models = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-3-27b-it:free",
    "google/gemma-3-4b-it:free",
    "google/gemma-3n-e4b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "qwen/qwen3-4b:free",
    "qwen/qwen3-coder:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "openchat/openchat-7b:free",
]

print("Testing each FREE model (this takes ~2 minutes)...\n")

working = []

for model in models:
    print(f"  Testing {model}... ", end="", flush=True)
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 10,
            },
            timeout=15,
        )
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            print(f"YES! -> {answer[:30]}")
            working.append(model)
        else:
            code = response.status_code
            print(f"NO ({code})")
    except Exception as e:
        print(f"NO (timeout)")

    time.sleep(1)  # Small delay between requests

print(f"\n{'='*50}")
if working:
    print(f"WORKING MODELS ({len(working)}):")
    for m in working:
        print(f"  {m}")
    print(f"\nBEST CHOICE: {working[0]}")
    print(f"\nUpdate your .env:")
    print(f"  OPENROUTER_MODEL={working[0]}")
else:
    print("No models working right now. Wait 5 minutes and try again.")