# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| trained | dry_strategy_sprint | 0.508 | 0.019 |
| trained | weather_roulette | 0.550 | 0.012 |
| trained | late_safety_car | 0.543 | 0.010 |
| trained | championship_decider | 0.506 | 0.009 |

Scores are deterministic environment rewards averaged across held-out seeds.
`trained` is the model loaded from `--model` (HF Hub repo or local transformers checkpoint). For local-smoke runs without a real checkpoint it falls back to a deliberately weaker scripted policy that demonstrates the gap to expert.