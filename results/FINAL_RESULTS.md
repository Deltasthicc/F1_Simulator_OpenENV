# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| trained | dry_strategy_sprint | 0.523 | 0.006 |
| trained | weather_roulette | 0.516 | 0.032 |
| trained | late_safety_car | 0.559 | 0.018 |
| trained | championship_decider | 0.365 | 0.159 |

Scores are deterministic environment rewards averaged across held-out seeds.
`trained` is the model loaded from `--model` (HF Hub repo or local transformers checkpoint). For local-smoke runs without a real checkpoint it falls back to a deliberately weaker scripted policy that demonstrates the gap to expert.