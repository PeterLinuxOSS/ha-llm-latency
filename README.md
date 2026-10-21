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


## Latest run — EN — 2026-10-21T16:48:23+00:00

_24 prompts, 24 calls per model._

| Model | Reasoning | Median | Mean | p95 | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| gemini-3.5-flash-lite | default | 0.52s | 0.55s | 0.68s | 0.42s | 0.76s |
| mistral-small-3.2 | default | 0.57s | 0.62s | 0.92s | 0.40s | 1.08s |
| gemini-2.5-flash | default | 0.58s | 0.68s | 1.29s | 0.45s | 1.30s |
| gemini-3.1-flash-lite | default | 0.70s | 0.74s | 1.02s | 0.54s | 1.16s |
| gpt-5.4-nano | default | 0.71s | 0.75s | 1.15s | 0.55s | 1.19s |
| llama-3.3-70b | default | 0.72s | 0.88s | 1.52s | 0.19s | 1.75s |
| gpt-5.4-mini | default | 0.75s | 0.89s | 1.57s | 0.53s | 2.06s |
| claude-haiku-5-5 | default | 1.22s | 1.28s | 1.76s | 0.93s | 2.03s |
| gpt-5-nano | default | 1.68s | 1.71s | 1.84s | 1.53s | 2.04s |
| claude-haiku-4-5 | default | 1.68s | 1.47s | 1.98s | 0.60s | 2.04s |
| deepseek-chat-v3.1 | default | 2.04s | 2.33s | 4.39s | 0.71s | 4.68s |
| gemini-3.5-flash | default | 2.13s | 2.24s | 3.37s | 1.73s | 3.80s |
| claude-sonnet-5-5 | default | 2.40s | 2.39s | 2.96s | 1.85s | 3.35s |
| gpt-5-mini | default | 2.53s | 2.67s | 3.65s | 2.08s | 3.96s |
| gemini-3.8-flash | default | 3.36s | 3.42s | 4.68s | 2.56s | 4.87s |

## Median history

### Median history — EN

| Date | gemini-3.5-flash-lite | gpt-5.4-mini | gemini-3.8-flash | claude-haiku-5-5 | claude-haiku-4-5 | gpt-5.4-nano | gpt-5-mini | gpt-5-nano | gemini-3.1-flash-lite | gemini-2.5-flash | gemini-3.5-flash | claude-sonnet-5-5 | deepseek-chat-v3.1 | llama-3.3-70b | mistral-small-3.2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-21 | 0.59s | 0.69s | 3.72s |  |  |  |  |  |  |  |  |  |  |  |  |
| 2026-10-21 | 0.58s | 0.76s | 3.65s | 1.19s | 1.56s | 0.68s | 2.70s | 1.97s | 0.70s | 0.58s | 2.25s |  |  |  |  |
| 2026-10-21 | 0.52s | 0.75s | 3.36s | 1.22s | 1.68s | 0.71s | 2.53s | 1.68s | 0.70s | 0.58s | 2.13s | 2.40s | 2.04s | 0.72s | 0.57s |

## Method

- `probe.py` sends each prompt in `prompts.txt` to each model in `models.yaml`,
  cycling to `--runs` calls (default 8), after one unmeasured warm-up call.
- Latency is `time.perf_counter()` around a single non-streaming request.
- `reasoning` in `models.yaml` toggles provider thinking/reasoning effort
  (gemini `off|low|medium|high`, openai `minimal|low|medium|high`).
- Numbers depend on network location and time of day; treat them as relative.


---

Vibecoded by Claude Code. MIT licensed.
