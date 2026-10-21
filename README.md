# HA LLM Latency

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


## Latest run — EN — 2026-10-21T16:35:46+00:00

_24 prompts, 24 calls per model._

| Model | Reasoning | Median | Mean | p95 | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| gemini-2.5-flash | default | 0.58s | 0.65s | 1.07s | 0.44s | 1.45s |
| gemini-3.5-flash-lite | default | 0.58s | 0.57s | 0.71s | 0.42s | 0.74s |
| gpt-5.4-nano | default | 0.68s | 0.73s | 1.03s | 0.54s | 1.07s |
| gemini-3.1-flash-lite | default | 0.70s | 0.71s | 0.90s | 0.51s | 0.96s |
| gpt-5.4-mini | default | 0.76s | 0.76s | 0.95s | 0.57s | 0.98s |
| claude-haiku-5-5 | default | 1.19s | 1.30s | 1.85s | 0.97s | 2.42s |
| claude-haiku-4-5 | default | 1.56s | 1.31s | 1.74s | 0.61s | 2.03s |
| gpt-5-nano | default | 1.97s | 2.07s | 2.75s | 1.72s | 2.97s |
| gemini-3.5-flash | default | 2.25s | 2.41s | 3.46s | 1.88s | 4.86s |
| gpt-5-mini | default | 2.70s | 2.76s | 3.23s | 2.29s | 3.90s |
| gemini-3.8-flash | default | 3.65s | 3.84s | 4.87s | 3.00s | 6.82s |

## Median history

### Median history — EN

| Date | gemini-3.5-flash-lite | gpt-5.4-mini | gemini-3.8-flash | claude-haiku-5-5 | claude-haiku-4-5 | gpt-5.4-nano | gpt-5-mini | gpt-5-nano | gemini-3.1-flash-lite | gemini-2.5-flash | gemini-3.5-flash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-21 | 0.59s | 0.69s | 3.72s |  |  |  |  |  |  |  |  |
| 2026-10-21 | 0.58s | 0.76s | 3.65s | 1.19s | 1.56s | 0.68s | 2.70s | 1.97s | 0.70s | 0.58s | 2.25s |

## Method

- `probe.py` sends each prompt in `prompts.txt` to each model in `models.yaml`,
  cycling to `--runs` calls (default 8), after one unmeasured warm-up call.
- Latency is `time.perf_counter()` around a single non-streaming request.
- `reasoning` in `models.yaml` toggles provider thinking/reasoning effort
  (gemini `off|low|medium|high`, openai `minimal|low|medium|high`).
- Numbers depend on network location and time of day; treat them as relative.


---

Vibecoded by Claude Code. MIT licensed.
