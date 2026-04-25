# F1 Strategist Qwen3 GRPO Checkpoint

This model is intended to act inside the F1 Strategist OpenEnv environment as a race
strategy agent. It emits one command per turn, such as `REQUEST_FORECAST`,
`PIT_NOW inter`, `SET_MODE push`, or `RADIO_DRIVER "Box this lap"`.

## Environment

- Repository: `Deltasthicc/F1_Simulator_OpenENV`
- Space: `Deltasthic/f1-strategist`
- Action schema: `models.F1Action`
- Observation schema: `models.F1Observation`
- Reward: six deterministic dimensions in `server/scoring.py`

## Training Recipe

The full intended run uses:

- Base model: `Qwen/Qwen3-4B`
- Method: SFT warm-start on expert trajectories, then TRL GRPO
- Hardware: 1x RTX 5090, CUDA 12.8
- Command:

```bash
python train.py \
  --backend trl \
  --model Qwen/Qwen3-4B \
  --task multi \
  --max-steps 500 \
  --batch-size 1 \
  --grad-accum 32 \
  --output-dir ./grpo_v1
```

For local pipeline smoke tests without GPU, use:

```bash
python train.py --backend local-smoke --model heuristic --task multi --max-steps 30
```

The local smoke backend validates the environment, reward curve plumbing, checkpoint
upload path, and evaluation artifacts. It is not a substitute for the published GRPO
checkpoint.

## Evaluation

Run:

```bash
python evaluate.py \
  --model Deltasthic/f1-strategist-qwen3-4b-grpo \
  --tasks dry_strategy_sprint weather_roulette late_safety_car championship_decider \
  --n-seeds 5 \
  --modes random untrained trained expert
```

Outputs:

- `results/eval_summary.json`
- `results/eval_curve.png`
- `results/FINAL_RESULTS.md`

## Limitations

This model is a hackathon research artifact for a simulated strategy environment. It is
not a real motorsport decision system and should not be used for safety-critical or
commercial race operations.
