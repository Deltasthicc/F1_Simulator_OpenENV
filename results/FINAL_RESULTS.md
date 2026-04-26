# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| random | dry_strategy_sprint | 0.400 | 0.124 |
| random | weather_roulette | 0.344 | 0.029 |
| random | late_safety_car | 0.332 | 0.029 |
| random | championship_decider | 0.209 | 0.024 |
| random | virtual_safety_car_window | 0.329 | 0.018 |
| random | tyre_cliff_management | 0.204 | 0.020 |
| untrained | dry_strategy_sprint | 0.509 | 0.055 |
| untrained | weather_roulette | 0.414 | 0.073 |
| untrained | late_safety_car | 0.525 | 0.140 |
| untrained | championship_decider | 0.269 | 0.008 |
| untrained | virtual_safety_car_window | 0.375 | 0.000 |
| untrained | tyre_cliff_management | 0.398 | 0.144 |
| trained | dry_strategy_sprint | 0.520 | 0.000 |
| trained | weather_roulette | 0.965 | 0.040 |
| trained | late_safety_car | 0.645 | 0.000 |
| trained | championship_decider | 0.555 | 0.025 |
| trained | virtual_safety_car_window | 0.471 | 0.109 |
| trained | tyre_cliff_management | 0.552 | 0.019 |
| expert | dry_strategy_sprint | 0.840 | 0.091 |
| expert | weather_roulette | 0.950 | 0.000 |
| expert | late_safety_car | 0.935 | 0.000 |
| expert | championship_decider | 0.965 | 0.000 |
| expert | virtual_safety_car_window | 0.965 | 0.000 |
| expert | tyre_cliff_management | 0.965 | 0.000 |

Scores are deterministic environment rewards averaged across held-out seeds.
`trained` is the model loaded from `--model` (HF Hub repo or local transformers checkpoint). For local-smoke runs without a real checkpoint it falls back to a deliberately weaker scripted policy that demonstrates the gap to expert.