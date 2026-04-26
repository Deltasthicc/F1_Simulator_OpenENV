# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| trained | dry_strategy_sprint | 0.520 | 0.000 |
| trained | weather_roulette | 0.719 | 0.213 |
| trained | late_safety_car | 0.599 | 0.030 |
| trained | championship_decider | 0.552 | 0.021 |

Scores are deterministic environment rewards averaged across held-out seeds.
`trained` is the model loaded from `--model` (HF Hub repo or local transformers checkpoint). For local-smoke runs without a real checkpoint it falls back to a deliberately weaker scripted policy that demonstrates the gap to expert.