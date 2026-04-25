# Execution State — F1 Strategist Hackathon

Updated after each phase gate. If anything kills the session, read this top-to-bottom to resume.

## Identity & infra
- Box: `anurag-vps`, user `anurag`
- GPU: RTX 5090, CUDA driver 13.2, 32 GB VRAM
- Venv: `~/.virtualenvs/f1-strategist` (python 3.12.3)
- Repo: `/home/anurag/projects/F1_Simulator_OpenENV` (branch `dev`)
- Port: env binds to `8765`
- Domain: `f1.chinnaboina.com` (via cloudflared tunnel)
- HF token: placeholder in `.env`, real value pending

## Milestones

- [x] Phase 0 — Pre-flight + repo prep
- [x] Phase 1 — Install training stack
- [x] Phase 2 — Re-verify env (164 tests + 6 scenarios)
- [x] Phase 3 — Cloudflare tunnel for f1.chinnaboina.com (LIVE)
- [x] Phase 4 — Generate SFT seed data (2450 turns)
- [⏸] Phase 5 — GRPO smoke run [PAUSED: GPU shared with friend; NaN issue at first generation needs --no-unsloth retry]
- [⏸] Phase 6 — Full GRPO (500 steps, Qwen3-4B) [BLOCKED on Phase 5]
- [x] Phase 7 — Landing page LIVE at https://f1.chinnaboina.com/ (CPU-only)
- [x] Phase 8 — HF Space LIVE (Deltasthic/f1-strategist serves landing page); checkpoint push deferred until Phase 6
- [⏸] Phase 9 — Eval against trained checkpoint [BLOCKED on Phase 6]
- [~] Phase 10 — Demo polish (README updated with live URLs; numbers + new GIFs after Phase 9)
- [~] Phase 11 — Pre-push hygiene done (secret scan ✅, no large files ✅, .env not tracked ✅, README links resolve ✅); final tag waits on training
- [~] Phase 12 — Historical replay loader stubbed (`scripts/build_historical_replay.py`, `data/historical_replays/`); leaderboard not yet

## Resume markers when GPU is free
**SIGNAL:** `nvidia-smi --query-gpu=memory.free --format=csv,noheader` returns >25 GB.
**RESUME AT:** Phase 5. First action: re-run smoke with `--no-unsloth` (Unsloth's patched generate triggers NaN on sm_120 — confirmed three identical CUDA asserts). Command:
```
tmux new -d -s smoke "source ~/.virtualenvs/f1-strategist/bin/activate && set -a && source .env && set +a && rm -rf grpo_smoke training_smoke.log && python train.py --backend trl --model Qwen/Qwen3-0.6B --task dry_strategy_sprint --max-steps 50 --batch-size 1 --grad-accum 8 --logging-steps 5 --save-steps 25 --no-unsloth --output-dir ./grpo_smoke 2>&1 | tee training_smoke.log"
```
If that also NaNs: lower `--temperature` 0.9→0.5 in train.py, or switch to Qwen3-1.7B (has real pad token, not the placeholder Qwen3-0.6B uses).

## Phase log

### Phase 0 — Pre-flight + repo prep ✅
- 2026-04-25 16:40 — venv created at `~/.virtualenvs/f1-strategist`
- 2026-04-25 16:41 — `.env` created from template, port=8765, HF_TOKEN=placeholder
- 2026-04-25 16:41 — `.env` confirmed gitignored
- Cloudflared inspection: existing tunnel `476cc98d-...` named `vijayrekha`, single ingress to `chinnaboina.com:80`
- User confirmed: Option A (extend existing tunnel)
- Ports 8765–8770 all free
- Nginx site `vijayrekha.conf` untouched

### Phase 1 — Install training stack ✅
- 2026-04-25 16:50 — torch 2.10.0+cu128 installed, sm_120 matmul verified on RTX 5090
- 2026-04-25 16:55 — repo installed editable; openenv-core 0.2.3 in
- 2026-04-25 17:00 — trl 0.24.0, transformers 5.5.0, peft 0.19.1, accelerate 1.13.0, datasets 4.3.0
- 2026-04-25 17:05 — unsloth 2026.4.8 + unsloth_zoo 2026.4.9 installed
- 2026-04-25 17:08 — `requirements.lock` written (165 packages)
- Note: Flash Attention 2 not present, Unsloth uses Xformers (no perf impact)

### Phase 2 — Re-verify env ✅
- 2026-04-25 17:00 — 164/164 tests pass (more than docs claimed 130 — `test_scenarios_extended` adds coverage)
- 2026-04-25 17:01 — 6 scenarios discriminate (expert ≥0.88, panic ≤0.40)
- 2026-04-25 17:02 — Env booted on 127.0.0.1:8765, PID 473838 in background
- 2026-04-25 17:02 — All 20 expert traces present (4 scenarios × 5 seeds)

### Phase 3 — Cloudflare tunnel ✅ LIVE
- 2026-04-25 17:01 — DNS CNAME `f1.chinnaboina.com` → tunnel UUID 476cc98d
- 2026-04-25 17:05 — Backed up `/etc/cloudflared/config.yml` to `.bak.<ts>`
- 2026-04-25 17:05 — Replaced config (added f1.chinnaboina.com → localhost:8765 ingress, vijayrekha untouched)
- 2026-04-25 17:06 — `systemctl restart cloudflared` (reload not supported on this unit)
- 2026-04-25 17:06 — Both endpoints verified:
  - `https://chinnaboina.com` → 200 (vijayrekha alive)
  - `https://f1.chinnaboina.com/health` → 200 `{"status":"healthy"}`
- HF_TOKEN: real value confirmed in .env, `whoami()` returns `Deltasthic` (org account direct login)

## Open blockers
None — clear runway through training.
