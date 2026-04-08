"""Groq API wrapper with retry, backoff, and JSON mode."""

import json
import os
import time

from groq import Groq

MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.2
MAX_RETRIES = 3


def _client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY environment variable is not set.")
    return Groq(api_key=api_key)


def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """Call Groq with optional JSON mode. Returns the response text.

    Args:
        system_prompt: High-level instructions for the model.
        user_prompt: The specific request / context for this call.
        json_mode: When True, instructs the model to return valid JSON only
                   and retries once on parse failure.

    Returns:
        The model's response as a string (or validated JSON string if json_mode).
    """
    if json_mode:
        system_prompt = (
            system_prompt.rstrip()
            + "\n\nReturn valid JSON only, no markdown fences."
        )

    client = _client()

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = response.choices[0].message.content.strip()

            if json_mode:
                # Strip accidental markdown fences the model may still emit
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                    text = text.strip()
                # Validate JSON; raise ValueError to trigger retry
                json.loads(text)

            return text

        except (ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                print(f"[llm] JSON parse failed (attempt {attempt + 1}), retrying in {wait}s…")
                time.sleep(wait)

        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                print(f"[llm] API error (attempt {attempt + 1}): {exc}. Retrying in {wait}s…")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(
        f"LLM call failed after {MAX_RETRIES} attempts. Last error: {last_error}"
    )
