"""
LLM Service using OpenRouter FREE API.
Handles models that don't support system prompts.
"""
import requests
import time
from typing import Optional, Dict
from src.config.settings import get_settings
from src.utils.logger import app_logger as logger


class LLMService:
    """Call FREE LLM via OpenRouter."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.openrouter_api_key
        self.model = self.settings.openrouter_model
        logger.info(f"LLM Service: {self.model} (FREE)")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> Dict:
        """Generate response from LLM."""

        # Some free models don't support system messages
        # So we combine system + user into one message
        if system_prompt:
            full_prompt = f"Instructions: {system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        messages = [{"role": "user", "content": full_prompt}]

        start = time.time()

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )

        latency = time.time() - start

        if response.status_code != 200:
            error_msg = response.text[:300]
            logger.error(f"LLM error: {response.status_code} - {error_msg}")

            # If model fails, try fallback model
            fallback = self._try_fallback(messages, temperature, max_tokens)
            if fallback:
                return fallback

            raise Exception(f"LLM error: {response.status_code} - {error_msg}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        result = {
            "content": content,
            "model": self.model,
            "latency_seconds": round(latency, 2),
            "tokens_used": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": usage.get("total_tokens", 0),
            },
            "cost": 0.00,
        }

        logger.info(f"LLM response in {latency:.1f}s | Cost: $0.00")
        return result

    def _try_fallback(self, messages, temperature, max_tokens) -> Optional[Dict]:
        """Try fallback free models if primary fails."""
        fallbacks = [
            "meta-llama/llama-3.2-3b-instruct:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "google/gemma-3-12b-it:free",
            "qwen/qwen3-4b:free",
        ]

        for model in fallbacks:
            if model == self.model:
                continue

            logger.info(f"Trying fallback model: {model}")

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})

                    logger.info(f"Fallback {model} worked!")

                    return {
                        "content": content,
                        "model": model,
                        "latency_seconds": 0,
                        "tokens_used": {
                            "prompt": usage.get("prompt_tokens", 0),
                            "completion": usage.get("completion_tokens", 0),
                            "total": usage.get("total_tokens", 0),
                        },
                        "cost": 0.00,
                    }
            except Exception:
                continue

        return None