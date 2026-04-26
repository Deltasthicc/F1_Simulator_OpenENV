# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| random | dry_strategy_sprint | 0.347 | 0.007 |
| random | weather_roulette | 0.325 | 0.022 |
| random | late_safety_car | 0.312 | 0.022 |
| random | championship_decider | 0.200 | 0.010 |
| untrained | dry_strategy_sprint | 0.506 | 0.061 |
| untrained | weather_roulette | 0.378 | 0.000 |
| untrained | late_safety_car | 0.420 | 0.175 |
| untrained | championship_decider | 0.275 | 0.010 |
| trained | dry_strategy_sprint | 0.771 | 0.114 |
| trained | weather_roulette | 0.935 | 0.000 |
| trained | late_safety_car | 0.935 | 0.000 |
| trained | championship_decider | 0.535 | 0.000 |
| expert | dry_strategy_sprint | 0.771 | 0.114 |
| expert | weather_roulette | 0.950 | 0.000 |
| expert | late_safety_car | 0.935 | 0.000 |
| expert | championship_decider | 0.965 | 0.000 |

Scores are deterministic environment rewards averaged across held-out seeds.
`trained` is the model loaded from `--model` (HF Hub repo or local transformers checkpoint). For local-smoke runs without a real checkpoint it falls back to a deliberately weaker scripted policy that demonstrates the gap to expert.