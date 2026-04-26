# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| trained | dry_strategy_sprint | 0.520 | 0.000 |
| trained | weather_roulette | 0.406 | 0.064 |
| trained | late_safety_car | 0.145 | 0.000 |
| trained | championship_decider | 0.233 | 0.059 |

Scores are deterministic environment rewards averaged across held-out seeds.
`trained` is the model loaded from `--model` (HF Hub repo or local transformers checkpoint). For local-smoke runs without a real checkpoint it falls back to a deliberately weaker scripted policy that demonstrates the gap to expert.