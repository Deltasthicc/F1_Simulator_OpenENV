# Phase 9 — DONE ✅

Held-out eval **(4 tasks × 5 seeds, weighted_final score)**

| mode | dry | weather | safety_car | champ | avg |
|---|---:|---:|---:|---:|---:|
| random | 0.40 | 0.34 | 0.33 | 0.21 | 0.32 |
| untrained | 0.51 | 0.41 | 0.53 | 0.27 | 0.43 |
| trained | 0.75 | 0.94 | 0.94 | 0.54 | 0.79 |
| expert | 0.84 | 0.95 | 0.94 | 0.96 | 0.92 |

- Trained beats untrained on every task; biggest jump on `weather_roulette` (+0.52 absolute).
- Gap to expert ceiling: trained avg=0.79, expert avg=0.92, random avg=0.32.
- Story line: GRPO closed about **78%** of the random→expert gap.
- Files: `results/eval_summary.json`, `results/eval_curve.png`, `results/training_loss_curve.png`, `results/FINAL_RESULTS.md`.