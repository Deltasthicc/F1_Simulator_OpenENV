# Final Results

| mode | task | mean | std |
|---|---:|---:|---:|
| random | dry_strategy_sprint | 0.400 | 0.124 |
| random | weather_roulette | 0.344 | 0.029 |
| random | late_safety_car | 0.332 | 0.029 |
| random | championship_decider | 0.209 | 0.024 |
| untrained | dry_strategy_sprint | 0.509 | 0.055 |
| untrained | weather_roulette | 0.414 | 0.073 |
| untrained | late_safety_car | 0.525 | 0.140 |
| untrained | championship_decider | 0.269 | 0.008 |
| trained | dry_strategy_sprint | 0.749 | 0.112 |
| trained | weather_roulette | 0.935 | 0.000 |
| trained | late_safety_car | 0.935 | 0.000 |
| trained | championship_decider | 0.535 | 0.000 |
| expert | dry_strategy_sprint | 0.840 | 0.091 |
| expert | weather_roulette | 0.950 | 0.000 |
| expert | late_safety_car | 0.935 | 0.000 |
| expert | championship_decider | 0.965 | 0.000 |

Scores from real GRPO checkpoint `grpo_v1/checkpoint-500` (Qwen3-4B + LoRA, 500 GRPO steps).
`trained` is the actual fine-tuned model loaded via transformers + PEFT.
