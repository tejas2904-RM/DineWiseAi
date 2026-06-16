from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


class GroqAdapter:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout_seconds: int = 20):
        self.api_key = self._sanitize_api_key(api_key or os.getenv("GROQ_API_KEY"))
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.timeout_seconds = timeout_seconds
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required")

    @staticmethod
    def _sanitize_api_key(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        # Remove common accidental wrappers and invisible characters.
        cleaned = value.strip().strip("\"'").replace("\ufeff", "")
        return cleaned or None

    def generate(self, prompt: str) -> Dict[str, Any]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Return strictly JSON output."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
        if resp.status_code == 401:
            raise ValueError(
                "Groq authentication failed (401 invalid_api_key). "
                "Verify the key is an active Groq API key for your account/project."
            )
        resp.raise_for_status()
        data = resp.json()
        usage = data.get("usage", {})
        return {
            "content": data["choices"][0]["message"]["content"],
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "model": data.get("model", self.model),
        }
