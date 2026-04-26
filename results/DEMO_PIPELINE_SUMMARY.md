# Demo pipeline summary

Total wall-clock: 196.7s

## Held-out evaluation

| family | random | untrained | **trained** | expert |
|---|---:|---:|---:|---:|
| dry strategy sprint | 0.347 | 0.506 | **0.771** | 0.771 |
| weather roulette | 0.325 | 0.378 | **0.935** | 0.950 |
| late safety car | 0.312 | 0.420 | **0.935** | 0.935 |
| championship decider | 0.200 | 0.275 | **0.535** | 0.965 |

## Pipeline steps

| step | status | time |
|---|---|---:|
| [1/5] held-out evaluation | ok | 3.5s |
| [2/5] training curve | ok | 1.9s |
| [3/5] track grid + per-track GIFs | ok | 71.9s |
| [3b/5] race story chart | ok | 3.3s |
| [4/5] before/after — dry_strategy_sprint | ok | 25.6s |
| [4/5] before/after — weather_roulette | ok | 28.3s |
| [4/5] before/after — late_safety_car | ok | 28.3s |
| [4/5] before/after — championship_decider | ok | 33.8s |

## Artifacts produced

- `results/eval_curve.png` — annotated bar chart with Δ-improvement arrows
- `results/training_loss_curve.png` — smoothed reward curve + log-scale loss
- `results/track_grid.png` — trained policy across 8 tracks
- `captures/before_after_*.gif` — paired untrained-vs-trained for each family
- `captures/<task>__<track>_*_seed*.gif` — individual per-track demos