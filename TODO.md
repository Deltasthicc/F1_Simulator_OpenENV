# F1 Strategist — Checkpoint Tracker

Submission: **Meta PyTorch OpenEnv Hackathon Grand Finale**, Bangalore, April 25–26, 2026.

Authors: Shashwat Rajan, Tanish Shitanshu.
Repo (planned): `Deltasthicc/f1-strategist`.
HF Space (planned): `Deltasthic/f1-strategist`.

> Person 1 = Shashwat (Environment / Physics / Visualisation).
> Person 2 = Tanish (Training / Evaluation / Demo).
> Detailed per-person queues: [`docs/person1-tasks.md`](docs/person1-tasks.md), [`docs/person2-tasks.md`](docs/person2-tasks.md).

---

## Rubric: Minimum Requirements (gating)

These are the four non-negotiables from the official judging guide. Everything else
in this file is in service of these four.

- [ ] **W1** Uses latest OpenEnv (`openenv-core>=0.2.3`).
- [ ] **W1** Minimal TRL training script runnable in Colab. See `notebooks/f1_strategist_training_colab.ipynb`.
- [ ] **W2** Environment hosted on HuggingFace Spaces. See [`DEPLOY_SPACE.md`](DEPLOY_SPACE.md).
- [ ] **W3** Mini-blog on Hugging Face *or* YouTube video <2 min. Drafts in `demo-assets/`.
- [ ] **W4** README links to all of: HF Space, Colab notebook, blog, video, training plots, results table.

## Current Scoring Estimate

Pre-build state: **~0 / 100** (no env yet, no training).
Post-Phase-3 (training curve exists): target **70 / 100**.
Post-Phase-4 (postmortem ablation + polish): target **80–90 / 100**.

---

## Phase Tracker

> Phases mirror [`docs/build-order.md`](docs/build-order.md). Do not advance to the next phase
> if the current one is incomplete. Phase 3 is the gate everything else hinges on.

### Phase 0 — Repo Bootstrap (Person 1 + Person 2, parallel)
- [x] Decide layout (mirrors OpsTwin)
- [x] Decide theme (#2 primary, #3.1 secondary)
- [x] Decide action space (strategic only, no driving)
- [x] Decide six scoring dimensions
- [x] Pick five candidate tracks (Monza, Monaco, Catalunya, Spa-substitute, Silverstone-substitute via racetrack-database)
- [ ] **`git init` + first commit of doc skeleton**  (Person 2)
- [ ] **Create empty HF Space `Deltasthic/f1-strategist` (Docker SDK)**  (Person 2, see [`DEPLOY_SPACE.md`](DEPLOY_SPACE.md))
- [ ] **Run `scripts/extract_track_csvs.py` to populate `data/tracks/`**  (Person 1)
- [ ] **Run `scripts/calibrate_opponent_pace.py` to generate `data/opponent_pace_calibration.json`**  (Person 2)

### Phase 1 — Environment Skeleton (Person 1 owns)
Goal: `reset()/step()` loop works end-to-end. No real physics or scenarios yet.

- [ ] Implement `models.py` — `F1Action`, `F1Observation`, `F1State` (Pydantic).
- [ ] Port `server/app.py` from OpsTwin — single shared env singleton, FastAPI on 8000.
- [ ] Port `client.py` from OpsTwin — thin `EnvClient` subclass.
- [ ] Implement `server/environment.py` skeleton — `reset/step/_obs/_exec/_load` returning stubs.
- [ ] Implement `server/track.py` minimal — load one track CSV, expose centerline + length.
- [ ] Implement `server/physics.py` v0 — naive constant-pace lap-time, no tyre wear yet.
- [ ] Wire all action handlers as stubs returning `(0.0, "stub")`.
- [ ] `tests/test_environment.py` — assert `reset()` returns valid `F1Observation`, one `step` works.
- [ ] `tests/smoke_http.py` — assert HTTP `/reset`, `/step`, `/health` return 200.

**Exit criteria:** Server starts, one episode runs to `done`, score is computable (even if 0).

### Phase 2 — Physics + Scenarios + Reward (Person 1 + Person 2 split)
Goal: deterministic scoring discriminates good from bad strategy on three hand-authored scenarios.

- [ ] **Person 1**: `server/physics.py` v1 — tyre wear curves per compound, fuel burn, dirty-air drag.
- [ ] **Person 1**: `server/opponents.py` — rule-based opponents with pace + stint plans.
- [ ] **Person 1**: `server/weather.py` — pre-rolled weather and SC events from seed.
- [ ] **Person 1**: `server/scenarios.py` — three hand-authored scenario dicts (see [`docs/scenarios.md`](docs/scenarios.md)).
- [ ] **Person 1**: `server/hidden_state.py` — port HiddenStateLayer from OpsTwin.
- [ ] **Person 2**: `server/scoring.py` — six pure functions + `compute_multi_objective_scores()` (see [`docs/reward-model.md`](docs/reward-model.md)).
- [ ] **Person 2**: `baselines/expert_solver.py` — rule-based gold strategist hitting ≥0.92 on all three scenarios.
- [ ] **Person 2**: dump expert trajectories as `baselines/trajectories/*.jsonl`.
- [ ] **Person 1**: `tests/smoke_all_scenarios.py` — verify expert sequences score ≥0.85, panic sequences score ≤0.40.

**Exit criteria:** Expert solver works, reward signal is clearly discriminative (≥0.45 spread).

### Phase 3 — Training (HIGHEST PRIORITY)
Goal: at least one GRPO reward curve showing improvement. This is what judges will ask about.

- [ ] **Person 2**: `train.py` — TRL GRPO with `environment_factory`, Qwen3-4B + Unsloth + LoRA.
- [ ] **Person 2**: smoke run on RTX 5090 — 50 steps, confirm reward curve trends up.
- [ ] **Person 2**: full run — 500 steps minimum, 3-stage curriculum if needed (see [`TRAINING.md`](TRAINING.md)).
- [ ] **Person 2**: `evaluate.py` — held-out seeds, baseline vs trained vs random vs expert bar chart.
- [ ] **Person 2**: `notebooks/f1_strategist_training_colab.ipynb` — Colab-runnable smoke version.
- [ ] **Person 2**: push trained checkpoint to HF Hub (`Deltasthic/f1-strategist-qwen3-4b-grpo`).
- [ ] **Person 2**: produce `results/training_loss_curve.png`, `results/eval_curve.png`, `results/eval_summary.json`.

**Exit criteria:** Reward curve exists. Trained policy measurably outperforms untrained (≥0.20 average improvement). HF checkpoint published.

### Phase 4 — Self-Improvement Story (stretch, Person 1)
Goal: postmortem memory loop produces a measurable additional improvement delta.

- [ ] **Person 1**: `server/postmortem.py` — port from OpsTwin, append-only `.jsonl` storage.
- [ ] **Person 1**: hook generation into `environment.py` on `_done = True`.
- [ ] **Person 1**: inject top-2 postmortem hints into `reset()` observation under `memory_hints` field.
- [ ] **Person 2**: ablation eval — base trained policy vs postmortem-augmented on 10 held-out seeds.

**Exit criteria:** Memory retrieval works. Augmented policy shows measurable improvement.

### Phase 5 — Polish + Demo + Deploy (Person 1 + Person 2 parallel)
- [ ] **Person 1**: `server/visualizer.py` — matplotlib top-down replay → GIF/MP4 of any rollout.
- [ ] **Person 1**: render before/after visualisations of one trained vs untrained episode.
- [ ] **Person 1**: `server/generator.py` — procedural seed-deterministic scenario variants.
- [ ] **Person 1**: enable Gradio web UI (`ENABLE_WEB_INTERFACE=1` in Dockerfile).
- [ ] **Person 2**: `demo-assets/blog-post.md` — final polish, ≥600 words.
- [ ] **Person 2**: `demo-assets/video-script.md` + record video <2 min.
- [ ] **Person 2**: deploy HF Space (see [`DEPLOY_SPACE.md`](DEPLOY_SPACE.md)).
- [ ] **Person 2**: smoke-test live Space via `tests/smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space`.
- [ ] **Person 2**: publish blog on HF, video on YouTube; update README links.
- [ ] **Both**: walk through [`PRE_PUSH_CHECKLIST.md`](PRE_PUSH_CHECKLIST.md) before final tag.

---

## Pre-Onsite Checklist (must complete before April 25)

- [ ] Phases 1 and 2 complete locally (no GPU needed)
- [ ] `train.py` written and unit-smoke-tested locally on Qwen3-0.6B
- [ ] Expert trajectories generated and stored
- [ ] At least one short reward curve from a 30-step smoke run
- [ ] `evaluate.py` works against random + untrained + expert
- [ ] `data/tracks/*.csv` and `data/*.json` populated and committed
- [ ] HF Space exists and serves a hello-world `/reset`
- [ ] Phase 3 full run is ready to launch on the RTX 5090 on Day 1

Phase 3 full training run happens **on-site (Apr 25–26)** with HuggingFace compute credits
and the personal RTX 5090 server.

---

## Known Risks

- **Reward hacking via excessive INSPECT actions** — agent could spam `INSPECT_TYRE_DEGRADATION` for the +0.02 bonus. Mitigation: revelation reward fires only on *new* hidden-state info; subsequent inspect calls return same info but pay 0.0. Already in design.
- **Lap-time model overfit** — if the physics is too deterministic, the optimal strategy collapses to a hardcoded sequence and there's nothing to learn. Mitigation: per-lap noise on tyre wear and dirty-air drag, plus per-seed opponent pace jitter.
- **Long-horizon credit assignment** — GRPO may struggle when the only meaningful reward is at race end. Mitigation: dense per-step shaping rewards (issue resolutions, inspections, mode-match bonuses) plus the delayed-credit pattern from OpsTwin.
- **Colab T4 OOM on Qwen3-4B** — the Colab notebook needs to use the smaller Qwen3-0.6B / Qwen3-1.7B path with QLoRA. The full 4B run goes only on the 5090.

---

## Deploy Queue (commands the user will run)

### Git remote setup
- [ ] `git init && git add -A && git commit -m "scaffold"`
- [ ] Create GitHub repo `Deltasthicc/f1-strategist`
- [ ] `git remote add origin git@github.com:Deltasthicc/f1-strategist.git && git push -u origin main`

### Deploy to HuggingFace Space (see [`DEPLOY_SPACE.md`](DEPLOY_SPACE.md))
- [ ] `huggingface-cli login`
- [ ] `huggingface-cli repo create f1-strategist --type space --space_sdk docker --organization Deltasthic`
- [ ] `git remote add hfspace https://huggingface.co/spaces/Deltasthic/f1-strategist`
- [ ] `git push hfspace main:main`
- [ ] `python tests/smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space`
- [ ] Save URL to `demo-assets/hf-space-link.txt`

### Colab notebook smoke
- [ ] Open `notebooks/f1_strategist_training_colab.ipynb` in Colab (Free T4)
- [ ] Run all cells, confirm reward curve + sample rollout print appear
- [ ] Should take ~6–8 min on Qwen3-0.6B; do not attempt Qwen3-4B on Colab

---

## Done

- [x] Decided architecture (transplant OpsTwin shape; new domain).
- [x] Confirmed OpenEnv 0.2.3 is the target version.
- [x] Confirmed RTX 5090 32GB single-GPU is the training target.
- [x] Confirmed strategy-LLM framing (no driving control).
- [x] Confirmed five tracks, three hand-authored scenarios + stretch.
- [x] Doc skeleton written: README, CLAUDE, TODO, TRAINING, GPU_HANDOFF, DEPLOY_SPACE, PRE_PUSH_CHECKLIST, architecture, build-order, scenarios, reward-model, physics-model, person1-tasks, person2-tasks.
