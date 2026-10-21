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


## Latest run — EN — 2026-10-21T16:14:46+00:00

_8 prompts, 8 calls per model._

| Model | Reasoning | Median | Mean | p95 | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| gemini-3.5-flash-lite | default | 0.65s | 0.68s | 0.97s | 0.50s | 1.09s |
| gpt-5.4-mini | default | 0.69s | 0.71s | 0.89s | 0.55s | 0.90s |
| gemini-3.8-flash-low | low | 3.35s | 3.67s | 5.36s | 1.86s | 5.41s |
| gemini-3.8-flash | default | 3.47s | 3.58s | 4.30s | 2.78s | 4.58s |
| gemini-3.8-flash-off | off | 4.34s | 4.16s | 6.17s | 1.36s | 6.65s |

## Latest run — SK — 2026-10-21T16:12:53+00:00

_8 prompts, 8 calls per model._

| Model | Reasoning | Median | Mean | p95 | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| gemini-3.5-flash-lite | default | 0.63s | 0.62s | 0.73s | 0.46s | 0.74s |
| gpt-5.4-mini | default | 0.74s | 0.78s | 0.94s | 0.65s | 0.95s |
| gemini-3.8-flash | default | 4.61s | 4.77s | 6.20s | 3.22s | 6.28s |
| gemini-3.8-flash-low | low | 4.68s | 4.69s | 6.36s | 2.15s | 6.48s |
| gemini-3.8-flash-off | off | 4.70s | 4.13s | 5.95s | 1.44s | 6.13s |

## Median history

### Median history — EN

| Date | gemini-3.8-flash | gemini-3.8-flash-low | gemini-3.8-flash-off | gemini-3.5-flash-lite | gpt-5.4-mini |
| --- | --- | --- | --- | --- | --- |
| 2026-10-21 | 3.81s | 3.97s | 4.08s | 0.69s | 1.08s |
| 2026-10-21 | 3.47s | 3.35s | 4.34s | 0.65s | 0.69s |

## Method

- `probe.py` sends each prompt in `prompts.txt` to each model in `models.yaml`,
  cycling to `--runs` calls (default 8), after one unmeasured warm-up call.
- Latency is `time.perf_counter()` around a single non-streaming request.
- `reasoning` in `models.yaml` toggles provider thinking/reasoning effort
  (gemini `off|low|medium|high`, openai `minimal|low|medium|high`).
- Numbers depend on network location and time of day; treat them as relative.


---

Vibecoded by Claude Code. MIT licensed.
