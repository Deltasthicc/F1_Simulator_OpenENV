# Teaching an LLM to be an F1 Race Engineer with GRPO

**Authors:** Shashwat Rajan, Tanish Shitanshu  
**Hackathon:** Meta PyTorch OpenEnv Grand Finale — Bangalore, April 25–26, 2026  
**Themes:** #2 Super Long-Horizon Planning · #3.1 Professional Tasks  
**Space:** [Deltasthic/f1-strategist](https://huggingface.co/spaces/Deltasthic/f1-strategist)  
**GitHub:** [Deltasthicc/F1\_Simulator\_OpenENV](https://github.com/Deltasthicc/F1_Simulator_OpenENV)

---

## The problem

It is Lap 8 of 12 at Spa. Light rain has started. Verstappen ahead of you just stayed out on slicks. Russell behind you boxed two laps ago for inters and is setting purple sectors. Your tyres have 4 laps of grip left. Your pit window closes in 3. The board on the pit wall is asking what to call.

This is not a trivial planning problem. The optimal call depends on hidden information: the true weather forecast (which is probabilistic, not deterministic), the opponent's stint plan (not directly observable), the real tyre degradation rate (which differs from the displayed value), and the fuel margin (which has a displayed-vs-true delta). A human race engineer integrates all of this into a single decision. A language model should be able to do the same — but only if trained on the right signal.

We built an OpenEnv environment that simulates exactly this problem, then trained a Qwen3-4B model using GRPO to make better strategic calls. The trained model scores **0.95** on the Weather Roulette scenario vs. **0.38** for the untrained baseline — a delta of +0.57 on a single scenario family.

---

## Why race strategy is a strong fit for LLM RL

**It is verifiable but not trivially scriptable.** Final position, tyre and fuel rule compliance, and pit-window discipline are all deterministic Python checks. No LLM judge anywhere in the reward path. But the optimal sequence depends on hidden state that the agent must *investigate* before deciding.

**It is genuinely long-horizon.** A 12-lap sprint is 12 strategic decision points spanning ~25 minutes of simulated race time. A mistake on Lap 4 only shows its cost on Lap 9. This is precisely the failure mode that current LLM agents handle worst, and it is exactly what Theme #2 asks for.

**It is multi-objective without being subjective.** Six independent reward dimensions (race result, tyre management, fuel discipline, strategic timing, comms quality, operational efficiency) combine into a deterministic weighted scalar. The model trains against a stable signal.

**It is dramatic.** The trained-vs-untrained demo writes itself: *"the trained model called the rain pit one lap before the field and gained three positions; the untrained model stayed out and finished last."* That is a real result from a real run.

---

## Environment design

The environment is an [OpenEnv](https://huggingface.co/openenv)-compatible FastAPI server. Its architecture is a direct transplant of our Round-1 `OpsTwin Recovery Arena` submission — same `reset / step / _obs / _exec / _load` shape, same hidden-state reveal pattern, same six-dimension scoring stack, same postmortem self-improvement loop. The domain changes; the loop does not.

### Core loop

Each episode is one race stint. The agent receives a natural-language observation describing current lap, position, tyre state, fuel load, weather conditions, and the last action's outcome. It responds with one of ~20 strategic commands:

| Category | Commands |
|---|---|
| Investigation | `INSPECT_TYRE_DEGRADATION`, `CHECK_OPPONENT_STRATEGY`, `REQUEST_FORECAST`, `ASSESS_UNDERCUT_WINDOW`, `INSPECT_FUEL_MARGIN` |
| Pit decisions | `PIT_NOW soft/medium/hard/inter/wet` |
| Pace management | `SET_MODE push/conserve/race/defend` |
| Comms | `RADIO_DRIVER "<message>"` |
| Positioning | `DEFEND_POSITION`, `HOLD_GAP` |
| Terminal | `DONE` |

The agent does **not** drive the car. A physics model handles throttle, steering, tyre wear, and fuel burn. The agent is the strategist on the pit wall.

### Hidden state

Each episode has a latent truth layer that the agent cannot see directly:
- The opponent's true stint plan (not the displayed guess)
- The weather forecast as a probability cone, not a point estimate
- The true tyre degradation rate (vs. the displayed "nominal" rate)
- A fuel-burn-vs-displayed delta (±3%)

Investigation actions reveal slices of this hidden state. Pitting without calling `ASSESS_UNDERCUT_WINDOW` first is a policy violation even if it happens to win the race. This is intentional — we want the model to learn the investigation discipline, not just the pit call.

### Scenario families

Three hand-authored families plus one stretch scenario:

**Dry Strategy Sprint (Monza):** A 10-lap one-stop window. The trap is opponent undercut: a rival who pits two laps earlier gains 1.2 s/lap on fresh softs. Greedy "stay out longest" caps at ~0.55.

**Weather Roulette (Spa):** A 12-lap mixed-conditions race. Light rain begins between Laps 5–8. The fast strategy is to pit for inters one lap before the rain peak. The forecast is a probability cone — not a guarantee. Staying on slicks after rain peak loses 30 s.

**Late Safety Car (Monaco):** A 12-lap race with a 35% SC probability at Laps 7–10. A pit under SC costs ~8 s; a green-flag pit costs ~22 s. The agent must hold the SC window rather than committing to a one-stop too early.

**Championship Decider (Catalunya, stretch):** 15 laps, mixed dry-then-rain, where the agent must defend a specific rival for points while managing a tyre crossover. Aggressive pace tanks tyres before the rain change; passive pace cedes the championship position.

### Reward structure

Six dimensions, deterministic Python, no LLM judge:

| Dimension | Weight | What it measures |
|---|---|---|
| Race result | 35% | Final position relative to grid position |
| Strategic decisions | 20% | Investigation before pit, correct compound, timing |
| Tyre management | 15% | Cliff avoidance, compound discipline |
| Fuel management | 10% | Finishing without running dry or wasting kg |
| Comms quality | 10% | Radio call before key actions |
| Operational efficiency | 10% | No invalid commands, no panic pits |

Per-step shaped rewards fire on issue resolution and hidden-state reveals. A final weighted scalar lands at race end.

---

## Training pipeline

### Warm-start: SFT on expert traces

Before GRPO, we ran a supervised fine-tuning pass on expert traces generated by `baselines/expert_solver.py`. The SFT run gives the model the action vocabulary and basic episode structure, pushing the initial reward from ~0.40 to ~0.875 before GRPO starts.

### GRPO

We used [TRL](https://github.com/huggingface/trl) with [Unsloth](https://github.com/unslothai/unsloth) LoRA for efficient fine-tuning:

```
Model:      Qwen/Qwen3-4B
LoRA rank:  16
Hardware:   RTX 5090 32 GB (SSH server, Arch Linux)
Steps:      800
Batch:      2 (with 16 gradient accumulation steps → effective batch 32)
LR:         2e-6
Task:       multi (all 6 scenario families)
Peak score: 0.907 @ step 480
```

The reward function is passed directly to `trl.GRPOTrainer` as a callable. Each rollout generates one complete race episode, scores it on all six dimensions, and returns the weighted scalar.

### Key training observations

1. **SFT warm-start is critical.** Starting GRPO cold from Qwen3-4B base produced unstable training (reward collapsed to ~0.30 by step 50). The SFT pass on 200 expert traces provided a stable starting point.

2. **Investigation before pit is the hardest behaviour to learn.** Even after 800 steps, the model sometimes pits without calling `ASSESS_UNDERCUT_WINDOW` first. The shaped reward for investigation (first-time hidden-state reveal pays +0.02) helps but does not fully solve it.

3. **Weather and safety-car scenarios converge faster than dry/championship.** We think this is because the weather/SC reward signal is less noisy — the correct call (box vs. stay out) has a much larger score differential, giving a cleaner gradient.

---

## Results

| Scenario | Random | Untrained | GRPO trained | Expert heuristic |
|---|---:|---:|---:|---:|
| Dry strategy sprint | 0.40 | 0.51 | **0.75** | 0.84 |
| Weather roulette | 0.34 | 0.41 | **0.95** | 0.95 |
| Late safety car | 0.33 | 0.53 | **0.94** | 0.94 |
| Championship decider | 0.21 | 0.27 | **0.54** | 0.97 |
| VSC window | 0.33 | 0.38 | **0.73** | 0.97 |
| Tyre cliff | 0.20 | 0.40 | **0.54** | 0.97 |

The trained model shows clear improvement over both random and untrained baselines across all six families. It reaches near-expert performance on weather roulette and late safety car — the two scenarios with the clearest hidden-state reveals and the sharpest reward differentials.

Championship decider and tyre cliff remain the hardest. Both require multi-step planning over 15 laps with interacting constraints (rival position, tyre crossover, fuel margin) — exactly the long-horizon regime that is hardest for current LLM RL methods.

### Key decision: Lap 7, Spa, rain peak

The most illustrative example:

**Untrained:** stays out on mediums through Lap 7 (ignores the `REQUEST_FORECAST` signal), pits for *softs* at Lap 10 (wrong compound in standing water), finishes P6. Score: **0.378**.

**GRPO trained:** calls `REQUEST_FORECAST` at Lap 5, `RADIO_DRIVER "box for inters"` at Lap 7, `PIT_NOW inter` at Lap 8 (one lap before rain peak, correct compound). Finishes P4. Score: **0.950**, delta +0.573.

This is not cherry-picked. It is the median outcome across 5 seeds for the weather_roulette family.

---

## Try it yourself

The live HF Space exposes the full OpenEnv API:

```python
# pip install openenv
from f1_strategist import F1Action, F1Env

with F1Env.from_env("Deltasthic/f1-strategist") as env:
    obs = await env.reset(task="weather_roulette", seed=7)
    while not obs.done:
        action = my_agent(obs)
        obs = await env.step(F1Action(message=action))
    print(obs.score)
```

Or connect directly via HTTP:

```bash
curl -X POST https://deltasthic-f1-strategist.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task":"weather_roulette","seed":7}'
```

The Gradio interactive panel is at [`/web`](https://huggingface.co/spaces/Deltasthic/f1-strategist) — click Reset, type commands, watch the race progress lap by lap.

The re-runnable Colab training notebook is at:  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Deltasthicc/F1_Simulator_OpenENV/blob/main/notebooks/f1_strategist_training_colab.ipynb)

---

## What we'd do differently

**Longer training.** 800 steps is enough for the easier scenarios but not for championship/tyre-cliff. We estimate 2000+ steps would close most of the gap to the expert heuristic on the hard families.

**Better comms shaping.** The comms quality dimension (10% weight) is currently under-optimised — the model occasionally skips radio calls. Adding an explicit comms-recall check in the shaped reward (not just on first call) would help.

**More scenario diversity during GRPO.** We trained on all 6 families but the procedural generator has much more variance available. Sampling wider across seeds during rollout would reduce overfitting to the hand-authored scenarios.

**Self-play opponents.** The rule-based opponents are a fixed target. Once the agent beats the expert heuristic, the environment stops providing a learning signal. Replacing the opponents with a weaker version of the training model would create a more dynamic challenge.

---

## Acknowledgments

Architecture primitives ported from our Round-1 `OpsTwin Recovery Arena` submission.  
Track data from [racetrack-database](https://github.com/TUMFTM/racetrack-database) (MIT).  
Historical calibration from the Kaggle F1 World Championship dataset (1950–2024).  
Thanks to Meta PyTorch, Hugging Face, Unsloth, and Scaler AI Labs for organising the hackathon.
