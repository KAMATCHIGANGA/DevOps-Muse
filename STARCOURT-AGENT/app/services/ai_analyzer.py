
import time

import requests

from app.services.prompt import SRE_ANALYSIS_PROMPT

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def analyze_incident(evidence: str) -> str:
    prompt = SRE_ANALYSIS_PROMPT.format(evidence=evidence)

    start_time = time.perf_counter()

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=(5, 120),
        )

        response.raise_for_status()
        result = response.json().get("response", "").strip()

        if not result:
            raise RuntimeError("Ollama returned an empty response")

        return result

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Ollama request failed: {exc}"
        ) from exc
