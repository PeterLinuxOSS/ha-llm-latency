#!/usr/bin/env python3
"""Generate README.md from the newest results/*.json run.

Builds a latency leaderboard (fastest median first) plus a short history of the
median per model across past runs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

HEADER = """# HA LLM Latency

Chat-completion latency for the LLMs people run as **Home Assistant voice agents**.
Each model gets the same short home-control prompts; we record wall-clock latency.

> This is a **floor** latency: a bare API round trip with a small system prompt and
> **no tool calls**. Real Assist latency (large exposed-entity prompt + tool round
> trips) is higher — but this is a fair, repeatable way to rank models and compare
> reasoning-effort settings.

Run it yourself:

```sh
cp secrets.example.yaml secrets.yaml   # add your API keys
pip install -r requirements.txt
python probe.py
python build_readme.py
```
"""

METHOD = """## Method

- `probe.py` sends each prompt in `prompts.txt` to each model in `models.yaml`,
  cycling to `--runs` calls (default 8), after one unmeasured warm-up call.
- Latency is `time.perf_counter()` around a single non-streaming request.
- `reasoning` in `models.yaml` toggles provider thinking/reasoning effort
  (gemini `off|low|medium|high`, openai `minimal|low|medium|high`).
- Numbers depend on network location and time of day; treat them as relative.
"""

FOOTER = """---

Vibecoded by Claude Code. MIT licensed.
"""


def _runs() -> list[dict]:
    out = []
    for path in sorted(RESULTS.glob("*.json")):
        try:
            out.append(json.loads(path.read_text()))
        except json.JSONDecodeError:
            continue
    return out


def _leaderboard(latest: dict) -> str:
    rows = sorted(latest["results"], key=lambda r: r["median_s"])
    lines = [
        f"## Latest run — {latest['timestamp']}",
        "",
        f"_{latest['prompts']} prompts, {rows[0]['runs'] if rows else 0} calls per model._",
        "",
        "| Model | Reasoning | Median | Mean | p95 | Min | Max |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['reasoning']} | "
            f"{r['median_s']:.2f}s | {r['mean_s']:.2f}s | {r['p95_s']:.2f}s | "
            f"{r['min_s']:.2f}s | {r['max_s']:.2f}s |"
        )
    return "\n".join(lines)


def _history(runs: list[dict]) -> str:
    if len(runs) < 2:
        return ""
    names: list[str] = []
    for run in runs:
        for r in run["results"]:
            if r["name"] not in names:
                names.append(r["name"])
    lines = ["## Median history", "", "| Date | " + " | ".join(names) + " |",
             "| --- |" + " --- |" * len(names)]
    for run in runs[-10:]:
        by_name = {r["name"]: r["median_s"] for r in run["results"]}
        cells = [f"{by_name[n]:.2f}s" if n in by_name else "" for n in names]
        lines.append(f"| {run['timestamp'][:10]} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> None:
    runs = _runs()
    if not runs:
        raise SystemExit("No results yet. Run probe.py first.")
    latest = runs[-1]
    parts = [HEADER, _leaderboard(latest), _history(runs), METHOD, FOOTER]
    (ROOT / "README.md").write_text("\n\n".join(p for p in parts if p).strip() + "\n")
    print("Wrote README.md")


if __name__ == "__main__":
    main()
