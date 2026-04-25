# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| random | dry_strategy_sprint | 0.362 | 0.007 |
| random | weather_roulette | 0.325 | 0.022 |
| random | late_safety_car | 0.312 | 0.022 |
| random | championship_decider | 0.422 | 0.233 |
| untrained | dry_strategy_sprint | 0.506 | 0.061 |
| untrained | weather_roulette | 0.378 | 0.000 |
| untrained | late_safety_car | 0.420 | 0.175 |
| untrained | championship_decider | 0.305 | 0.040 |
| trained | dry_strategy_sprint | 0.965 | 0.000 |
| trained | weather_roulette | 0.950 | 0.000 |
| trained | late_safety_car | 0.935 | 0.000 |
| trained | championship_decider | 0.865 | 0.000 |
| expert | dry_strategy_sprint | 0.968 | 0.018 |
| expert | weather_roulette | 0.950 | 0.000 |
| expert | late_safety_car | 0.935 | 0.000 |
| expert | championship_decider | 0.965 | 0.000 |

Scores are deterministic environment rewards averaged across held-out seeds.
Note: `trained` in local smoke runs means the checkpoint policy path produced by `train.py --backend local-smoke`. Replace it with a published GRPO checkpoint after the RTX 5090 run.