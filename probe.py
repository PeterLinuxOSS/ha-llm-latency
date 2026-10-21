#!/usr/bin/env python3
"""Measure chat-completion latency for LLMs used as Home Assistant voice agents.

Sends a set of short home-control prompts to each configured model and records
wall-clock latency statistics. This is a *floor* latency: a bare API round trip
with a small system prompt and no tool calls, so real Assist latency (large
exposed-entity prompt + tool round trips) is higher. It is still a fair,
apples-to-apples way to compare models and reasoning-effort settings.

Usage:
    python probe.py                # all models in models.yaml
    python probe.py --only gemini-3.8-flash gpt-5.4-mini
    python probe.py --runs 8       # prompts are repeated/cycled to this many calls
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SYSTEM_PROMPT = (
    "You are a Home Assistant voice assistant. "
    "Carry out the request and reply with a short confirmation in plain text."
)


def _load_secret(name: str) -> str:
    secrets = yaml.safe_load((ROOT / "secrets.yaml").read_text())
    if name not in secrets:
        raise SystemExit(f"Missing '{name}' in secrets.yaml (see secrets.example.yaml)")
    return secrets[name]


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct
    lo = int(k)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


# --- provider adapters: each returns a zero-arg callable that does one request ---

def _gemini_caller(entry: dict):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_load_secret("google_api_key"))
    model = entry["model"]
    reasoning = entry.get("reasoning")
    thinking = None
    if reasoning == "off":
        thinking = types.ThinkingConfig(thinking_budget=0)
    elif reasoning in ("low", "medium", "high"):
        thinking = types.ThinkingConfig(thinking_level=reasoning)

    def call(prompt: str) -> None:
        cfg = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=200,
            thinking_config=thinking,
        )
        client.models.generate_content(model=model, contents=prompt, config=cfg)

    return call


def _openai_caller(entry: dict):
    import openai

    client = openai.OpenAI(api_key=_load_secret("openai_api_key"))
    model = entry["model"]
    reasoning = entry.get("reasoning")
    extra: dict = {}
    if reasoning in ("minimal", "low", "medium", "high"):
        extra["reasoning_effort"] = reasoning

    def call(prompt: str) -> None:
        client.chat.completions.create(
            model=model,
            max_completion_tokens=200,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            **extra,
        )

    return call


def _openrouter_caller(entry: dict):
    """OpenAI-compatible gateway — one key unlocks Grok, DeepSeek, Llama, Qwen, Mistral, ..."""
    import openai

    client = openai.OpenAI(
        api_key=_load_secret("openrouter_api_key"),
        base_url="https://openrouter.ai/api/v1",
    )
    model = entry["model"]

    def call(prompt: str) -> None:
        client.chat.completions.create(
            model=model,
            max_tokens=200,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

    return call


def _anthropic_caller(entry: dict):
    import anthropic

    client = anthropic.Anthropic(api_key=_load_secret("anthropic_api_key"))
    model = entry["model"]

    def call(prompt: str) -> None:
        client.messages.create(
            model=model,
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

    return call


ADAPTERS = {
    "gemini": _gemini_caller,
    "openai": _openai_caller,
    "anthropic": _anthropic_caller,
    "openrouter": _openrouter_caller,
}


def probe_model(entry: dict, prompts: list[str], runs: int) -> dict | None:
    adapter = ADAPTERS.get(entry["provider"])
    if adapter is None:
        print(f"  skip {entry['name']}: unknown provider {entry['provider']!r}")
        return None
    call = adapter(entry)
    # cycle prompts up to `runs` calls
    schedule = [prompts[i % len(prompts)] for i in range(runs)]
    try:
        call("Hi")  # warmup, not measured
    except Exception as exc:  # noqa: BLE001
        print(f"  ERROR {entry['name']}: {type(exc).__name__}: {str(exc)[:140]}")
        return None
    latencies: list[float] = []
    for prompt in schedule:
        start = time.perf_counter()
        try:
            call(prompt)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR {entry['name']}: {type(exc).__name__}: {str(exc)[:140]}")
            return None
        latencies.append(time.perf_counter() - start)
    stats = {
        "name": entry["name"],
        "provider": entry["provider"],
        "model": entry["model"],
        "reasoning": entry.get("reasoning", "default"),
        "runs": len(latencies),
        "median_s": round(statistics.median(latencies), 3),
        "mean_s": round(statistics.mean(latencies), 3),
        "p95_s": round(_percentile(latencies, 0.95), 3),
        "min_s": round(min(latencies), 3),
        "max_s": round(max(latencies), 3),
    }
    print(
        f"  {entry['name']:26s} median={stats['median_s']:.2f}s "
        f"mean={stats['mean_s']:.2f}s p95={stats['p95_s']:.2f}s"
    )
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", help="run only these model names")
    parser.add_argument("--runs", type=int, default=8, help="calls per model")
    parser.add_argument("--prompts", default="prompts.txt", help="prompt file")
    parser.add_argument("--label", help="language/prompt-set label (default: from filename)")
    args = parser.parse_args()

    label = args.label
    if not label:
        stem = Path(args.prompts).stem  # "prompts" or "prompts.sk"
        label = stem.split(".")[-1] if "." in stem else "en"

    models = yaml.safe_load((ROOT / "models.yaml").read_text())["models"]
    prompts = [
        line.strip()
        for line in (ROOT / args.prompts).read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if args.only:
        models = [m for m in models if m["name"] in args.only]

    print(f"Probing {len(models)} model(s) [{label}], {args.runs} calls each, {len(prompts)} prompts")
    results = [r for m in models if (r := probe_model(m, prompts, args.runs))]

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": platform.node(),
        "label": label,
        "system_prompt_chars": len(SYSTEM_PROMPT),
        "prompts": len(prompts),
        "results": results,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    path = ROOT / "results" / f"{stamp}-{label}.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {path.relative_to(ROOT)} ({len(results)} models)")


if __name__ == "__main__":
    main()
