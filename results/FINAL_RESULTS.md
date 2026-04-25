# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| random | dry_strategy_sprint | 0.368 | 0.030 |
| random | weather_roulette | 0.328 | 0.019 |
| random | late_safety_car | 0.315 | 0.019 |
| random | championship_decider | 0.192 | 0.014 |
| untrained | dry_strategy_sprint | 0.511 | 0.050 |
| untrained | weather_roulette | 0.438 | 0.086 |
| untrained | late_safety_car | 0.478 | 0.165 |
| untrained | championship_decider | 0.272 | 0.009 |
| trained | dry_strategy_sprint | 0.809 | 0.107 |
| trained | weather_roulette | 0.935 | 0.000 |
| trained | late_safety_car | 0.935 | 0.000 |
| trained | championship_decider | 0.535 | 0.000 |
| expert | dry_strategy_sprint | 0.809 | 0.107 |
| expert | weather_roulette | 0.950 | 0.000 |
| expert | late_safety_car | 0.935 | 0.000 |
| expert | championship_decider | 0.965 | 0.000 |

Scores are deterministic environment rewards averaged across held-out seeds.
`trained` is the model loaded from `--model` (HF Hub repo or local transformers checkpoint). For local-smoke runs without a real checkpoint it falls back to a deliberately weaker scripted policy that demonstrates the gap to expert.