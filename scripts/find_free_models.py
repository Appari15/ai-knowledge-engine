import requests

response = requests.get("https://openrouter.ai/api/v1/models")
models = response.json()["data"]

print("FREE MODELS AVAILABLE RIGHT NOW:")
print("=" * 60)

free_models = []
for m in models:
    pricing = m.get("pricing", {})
    prompt_price = float(pricing.get("prompt", "1"))
    completion_price = float(pricing.get("completion", "1"))
    if prompt_price == 0 and completion_price == 0:
        name = m["id"]
        free_models.append(name)
        print(f"  {name}")

print(f"\nTotal free models: {len(free_models)}")
print("\nCopy one of these and paste it in your .env file as OPENROUTER_MODEL")