"""
Model Manager
Dynamically fetches available free models from OpenRouter API at startup.
Also supports Ollama local models.
"""

import os
import time
import httpx
from typing import Optional

# ── Technique Prompt Builders ─────────────────────────────────────────────────

def build_prompt(prompt: str, technique: str, system_prompt: Optional[str]) -> tuple[str, str]:
    base_system = system_prompt or "You are a helpful, knowledgeable assistant."

    if technique == "zero_shot":
        return base_system, prompt
    elif technique == "one_shot":
        example = (
            "Example:\nUser: What is the capital of France?\n"
            "Assistant: The capital of France is Paris.\n\nNow answer:\n"
        )
        return base_system, example + prompt
    elif technique == "few_shot":
        examples = (
            "Examples of high-quality responses:\n\n"
            "Q: Explain photosynthesis simply.\n"
            "A: Plants convert sunlight, CO2 and water into glucose.\n\n"
            "Q: What is machine learning?\n"
            "A: Teaching computers to learn patterns from data.\n\n"
            "Now answer in the same concise style:\n"
        )
        return base_system, examples + prompt
    elif technique == "chain_of_thought":
        cot_system = base_system + (
            "\nThink step by step. Show reasoning before answering.\n"
            "Format: Thinking: [...] Answer: [...]"
        )
        return cot_system, f"Let's think through this carefully:\n\n{prompt}"
    elif technique == "role_play":
        role_system = (
            "You are a world-class expert with decades of experience. "
            "Explain with clarity, depth, and nuance."
        )
        return role_system, f"As an expert, please address:\n\n{prompt}"
    return base_system, prompt


# ── Provider metadata ─────────────────────────────────────────────────────────

PROVIDER_COLORS = {
    "meta-llama": "#7C3AED", "google": "#059669", "mistralai": "#4F8EF7",
    "microsoft": "#F59E0B", "deepseek": "#06B6D4", "qwen": "#F97316",
    "nvidia": "#84CC16", "openai": "#10B981", "anthropic": "#EC4899",
    "default": "#64748B",
}
PROVIDER_BADGES = {
    "meta-llama": "Meta AI", "google": "Google", "mistralai": "Mistral",
    "microsoft": "Microsoft", "deepseek": "DeepSeek", "qwen": "Alibaba",
    "nvidia": "NVIDIA", "openai": "OpenAI", "anthropic": "Anthropic",
}

OLLAMA_MODELS = {
    "ollama-llama3": {
        "label": "Llama 3 (Local)", "provider": "ollama", "model_id": "llama3",
        "description": "Llama 3 via Ollama — no API key needed.",
        "color": "#EF4444", "badge": "Local",
    },
    "ollama-mistral": {
        "label": "Mistral (Local)", "provider": "ollama", "model_id": "mistral",
        "description": "Mistral 7B via Ollama.", "color": "#EC4899", "badge": "Local",
    },
}

_dynamic_models_cache: dict = {}


def _model_id_to_key(model_id: str) -> str:
    return model_id.replace("/", "--").replace(":", "-")


def _parse_openrouter_model(m: dict) -> dict:
    model_id = m.get("id", "")
    name = m.get("name", model_id)
    description = (m.get("description") or f"Free model: {model_id}")[:120]
    provider_prefix = model_id.split("/")[0] if "/" in model_id else "default"
    color = PROVIDER_COLORS.get(provider_prefix, PROVIDER_COLORS["default"])
    badge = PROVIDER_BADGES.get(provider_prefix, provider_prefix.title())
    ctx = m.get("context_length", 0)
    ctx_label = f"{ctx//1000}K ctx" if ctx >= 1000 else f"{ctx} ctx"
    return {
        "label": name, "provider": "openrouter", "model_id": model_id,
        "description": f"{description[:100]} ({ctx_label})",
        "color": color, "badge": badge,
    }


async def fetch_free_models_from_openrouter() -> dict:
    global _dynamic_models_cache
    if _dynamic_models_cache:
        return _dynamic_models_cache

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get("https://openrouter.ai/api/v1/models", headers=headers)
            data = res.json()

        models = {}
        for m in data.get("data", []):
            mid = m.get("id", "")
            if not mid.endswith(":free"):
                continue
            key = _model_id_to_key(mid)
            models[key] = _parse_openrouter_model(m)

        if models:
            print(f"[ModelManager] Loaded {len(models)} free models from OpenRouter.")
            _dynamic_models_cache = models
            return models

    except Exception as e:
        print(f"[ModelManager] Could not fetch from OpenRouter: {e}")

    # Fallback
    fallback = {
        "nvidia--nemotron-3-super-120b-a12b-free": {
            "label": "Nemotron Super 120B", "provider": "openrouter",
            "model_id": "nvidia/nemotron-3-super-120b-a12b:free",
            "description": "NVIDIA 120B model (262K context).",
            "color": "#84CC16", "badge": "NVIDIA",
        },
    }
    _dynamic_models_cache = fallback
    return fallback


class ModelManager:

    def __init__(self):
        self._models: dict = {}

    async def _get_all_models(self) -> dict:
        if not self._models:
            cloud = await fetch_free_models_from_openrouter()
            self._models = {**cloud, **OLLAMA_MODELS}
        return self._models

    def available_models(self) -> dict:
        if _dynamic_models_cache:
            return {**_dynamic_models_cache, **OLLAMA_MODELS}
        return dict(OLLAMA_MODELS)

    async def available_models_async(self) -> dict:
        return await self._get_all_models()

    async def generate(self, model, prompt, technique, system_prompt, temperature, max_tokens,
                       top_p=1.0, top_k=0, frequency_penalty=0.0,
                       presence_penalty=0.0, repetition_penalty=1.0) -> dict:
        all_models = await self._get_all_models()
        if model not in all_models:
            return {"error": f"Unknown model: {model}", "response": "", "latency_ms": 0}

        cfg = all_models[model]
        system_msg, user_msg = build_prompt(prompt, technique, system_prompt)
        extra_params = dict(top_p=top_p, top_k=top_k,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty,
                            repetition_penalty=repetition_penalty)
        t0 = time.monotonic()
        try:
            if cfg["provider"] == "openrouter":
                response = await self._call_openrouter(cfg, system_msg, user_msg, temperature, max_tokens, extra_params)
            elif cfg["provider"] == "ollama":
                response = await self._call_ollama(cfg, system_msg, user_msg, temperature, max_tokens, extra_params)
            else:
                response = {"error": "Unknown provider", "response": ""}
        except Exception as exc:
            response = {"error": str(exc), "response": ""}

        response["latency_ms"] = round((time.monotonic() - t0) * 1000)
        response["technique"] = technique
        response["system_message"] = system_msg
        response["user_message"] = user_msg
        return response

    async def _call_openrouter(self, cfg, system_msg, user_msg, temperature, max_tokens, extra_params=None) -> dict:
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            return {"response": "No OPENROUTER_API_KEY found in .env", "error": "missing_api_key", "tokens_used": 0}

        ep = extra_params or {}
        body = {
            "model": cfg["model_id"],
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if ep.get("top_p", 1.0) != 1.0:
            body["top_p"] = ep["top_p"]
        if ep.get("top_k", 0) > 0:
            body["top_k"] = ep["top_k"]
        if ep.get("frequency_penalty", 0.0) != 0.0:
            body["frequency_penalty"] = ep["frequency_penalty"]
        if ep.get("presence_penalty", 0.0) != 0.0:
            body["presence_penalty"] = ep["presence_penalty"]
        if ep.get("repetition_penalty", 1.0) != 1.0:
            body["repetition_penalty"] = ep["repetition_penalty"]

        async with httpx.AsyncClient(timeout=90) as client:
            res = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://llm-explorer-toolkit",
                    "X-Title": "LLM Explorer Toolkit",
                },
                json=body,
            )
            data = res.json()

        if "error" in data:
            err = data["error"]
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            return {"response": "", "error": msg, "tokens_used": 0}

        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return {"response": content, "tokens_used": tokens, "error": None}

    async def _call_ollama(self, cfg, system_msg, user_msg, temperature, max_tokens, extra_params=None) -> dict:
        ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ep = extra_params or {}
        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
        if ep.get("top_p", 1.0) != 1.0:
            options["top_p"] = ep["top_p"]
        if ep.get("top_k", 0) > 0:
            options["top_k"] = ep["top_k"]
        if ep.get("repeat_penalty", 1.0) != 1.0:
            options["repeat_penalty"] = ep.get("repetition_penalty", 1.0)

        async with httpx.AsyncClient(timeout=180) as client:
            res = await client.post(
                f"{ollama_base}/api/chat",
                json={
                    "model": cfg["model_id"],
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    "options": options,
                    "stream": False,
                },
            )
            data = res.json()

        content = data.get("message", {}).get("content", "")
        return {"response": content, "tokens_used": data.get("eval_count", 0), "error": None}
