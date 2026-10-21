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


## Latest run — EN — 2026-10-21T16:22:40+00:00

_24 prompts, 24 calls per model._

| Model | Reasoning | Median | Mean | p95 | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| gemini-3.5-flash-lite | default | 0.59s | 0.61s | 0.87s | 0.42s | 0.98s |
| gpt-5.4-mini | default | 0.69s | 1.06s | 1.15s | 0.58s | 8.03s |
| gemini-3.8-flash | default | 3.72s | 3.83s | 4.73s | 2.75s | 5.12s |

## Method

- `probe.py` sends each prompt in `prompts.txt` to each model in `models.yaml`,
  cycling to `--runs` calls (default 8), after one unmeasured warm-up call.
- Latency is `time.perf_counter()` around a single non-streaming request.
- `reasoning` in `models.yaml` toggles provider thinking/reasoning effort
  (gemini `off|low|medium|high`, openai `minimal|low|medium|high`).
- Numbers depend on network location and time of day; treat them as relative.


---

Vibecoded by Claude Code. MIT licensed.
