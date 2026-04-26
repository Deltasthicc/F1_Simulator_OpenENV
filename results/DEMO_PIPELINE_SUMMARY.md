# Demo pipeline summary

Total wall-clock: 98.9s

## Held-out evaluation

| family | random | untrained | **trained** | expert |
|---|---:|---:|---:|---:|
| dry strategy sprint | 0.400 | 0.509 | **0.520** | 0.840 |
| weather roulette | 0.344 | 0.414 | **0.560** | 0.950 |
| late safety car | 0.332 | 0.525 | **0.550** | 0.935 |
| championship decider | 0.209 | 0.269 | **0.520** | 0.965 |

## Pipeline steps

| step | status | time |
|---|---|---:|
| [1/5] held-out evaluation | skipped (using existing results/eval_summary.json) | 0.0s |
| [2/5] training curve | ok | 2.5s |
| [3/5] track grid + per-track GIFs | ok | 33.4s |
| [3b/5] race story chart | ok | 4.5s |
| [4/5] before/after — dry_strategy_sprint | ok | 13.4s |
| [4/5] before/after — weather_roulette | ok | 15.2s |
| [4/5] before/after — late_safety_car | ok | 13.8s |
| [4/5] before/after — championship_decider | ok | 16.1s |

## Artifacts produced

- `results/eval_curve.png` — annotated bar chart with Δ-improvement arrows
- `results/training_loss_curve.png` — smoothed reward curve + log-scale loss
- `results/track_grid.png` — trained policy across 8 tracks
- `captures/before_after_*.gif` — paired untrained-vs-trained for each family
- `captures/<task>__<track>_*_seed*.gif` — individual per-track demos