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


## Latest run — 2026-10-21T16:05:52+00:00

_8 prompts, 8 calls per model._

| Model | Reasoning | Median | Mean | p95 | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| gemini-3.5-flash-lite | default | 0.69s | 0.72s | 0.89s | 0.62s | 0.92s |
| gpt-5.4-mini | default | 1.08s | 1.07s | 1.47s | 0.69s | 1.58s |
| gemini-3.8-flash | default | 3.81s | 3.97s | 5.21s | 3.13s | 5.56s |
| gemini-3.8-flash-low | low | 3.97s | 4.11s | 6.23s | 1.44s | 6.58s |
| gemini-3.8-flash-off | off | 4.08s | 3.80s | 5.83s | 1.51s | 6.04s |

## Method

- `probe.py` sends each prompt in `prompts.txt` to each model in `models.yaml`,
  cycling to `--runs` calls (default 8), after one unmeasured warm-up call.
- Latency is `time.perf_counter()` around a single non-streaming request.
- `reasoning` in `models.yaml` toggles provider thinking/reasoning effort
  (gemini `off|low|medium|high`, openai `minimal|low|medium|high`).
- Numbers depend on network location and time of day; treat them as relative.


---

Vibecoded by Claude Code. MIT licensed.
