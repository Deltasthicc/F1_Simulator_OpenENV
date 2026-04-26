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
- [x] Phase 5 — GRPO smoke (Shashwat already trained on another machine, smoke equivalent done)
- [x] Phase 6 — Full GRPO 500 steps Qwen3-4B (Shashwat — committed via main, merged into dev as `d763d0b`)
- [x] Phase 7 — Landing page LIVE at https://f1.chinnaboina.com/
- [x] Phase 8 — HF Space LIVE (Deltasthic/f1-strategist serves landing page)
- [x] Phase 9 — Eval against trained checkpoint (LoRA merged → `grpo_v1/merged-500/`, results at `results/eval_summary.json` + `results/eval_curve.png`)
- [x] Phase 10 — Iter 0–4: SFT v3 + GRPO v2 — **0.627 avg** champion (was 0.538). 5 bugs caught + fixed.
- [x] Phase 11a — Merged `origin/main` into `dev`, integrating UI/Space + keeping our model + bug-fixed eval
- [ ] Phase 11b — HF Hub model push: replace `Deltasthic/f1-strategist-qwen3-4b-grpo` with `grpo_v2/` adapter
- [ ] Phase 11c — Final commit + push to GitHub, submit hackathon form

## Champion model
**`grpo_v2/`** — SFT v3 (enriched obs, thinking-off render) → GRPO v2 (200 steps, no Unsloth, no vLLM, beta=0.005, num_generations=8). Avg eval **0.627** vs untrained 0.429 (+0.20). See `results/journey.png`, `results/scenario_breakdown.png`, `results/comparison_real.png`.

## Five bugs caught and fixed (the journey)
1. **Silent scripted-fallback bug** in main's `evaluate.py` → reported 0.79 was actually a hand-coded rule policy, never the model. Verified bit-exact match by running scripted policy in isolation.
2. **Qwen3 thinking-mode trap** — default reasoning-on with `max_new_tokens=64` → unparseable rambles → `parse_action()` fell through to STAY_OUT every step.
3. **Train/eval format mismatch** — flipping `enable_thinking=False` only at eval broke the chat-template prefix the model never saw.
4. **`format_obs` stripped scenario disambiguation** — model couldn't tell `late_safety_car` from `dry_strategy_sprint` at lap 0. Restored `obs.message` + `obs.hint`.
5. **Cold GRPO collapse** — vanilla GRPO from base Qwen3 plateaued at 0.54 (frac_reward_zero_std → 1.0). Fixed by SFT warm-start before GRPO (per `TRAINING.md`'s prescribed but skipped recipe).

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
_None._ git-lfs installed, weights pulled, LoRA merged into base, eval ran clean.

## Phase 9 — Eval results (4 tasks × 5 seeds, weighted_final score)

| mode | dry | weather | safety_car | champ | **avg** |
|---|---|---|---|---|---|
| random | 0.40 | 0.34 | 0.33 | 0.21 | **0.32** |
| untrained | 0.51 | 0.41 | 0.53 | 0.27 | **0.43** |
| trained | 0.52 | 0.56 | 0.55 | 0.52 | **0.54** |
| expert | 0.84 | 0.95 | 0.94 | 0.97 | **0.92** |

- Trained > untrained on every task; biggest jump championship_decider (+0.25)
- Trained std=0.0 across seeds (greedy decode, deterministic command sequence)
- Gap to expert ceiling: 0.38 — room to grow but clear training signal demonstrated

## Phase 6 — GRPO training (Shashwat's run, merged into dev)
- Commit: `eb9f4bf "Add trained Unsloth vLLM GRPO model and results"` (Shashwat, 2026-04-25 13:07)
- Steps: 500 (full target run)
- Saves: every 50 steps, 10 checkpoints (50, 100, 150, ..., 500)
- Reward trajectory (from `grpo_v1/checkpoint-500/trainer_state.json`):
  - Step 10  : reward=0.875, std=0.121
  - Step 500 : reward=0.893, std=0.095
  - Slight upward trend; std tightening (consistency improving)
  - `loss` collapsed to 0.0, `frac_reward_zero_std` reached 1.0 by end (policy converged)
- Train.py merge conflict resolved by adopting Shashwat's working config:
  `fast_inference=True, max_lora_rank=16, gpu_memory_utilization=0.30`

## Phase 7 — Landing page ✅
- `server/static/{index.html, style.css, app.js}` created with line-drawing animation
- `server/app.py` patched to serve `/` and `/static/*` (route override for openenv's redirect)
- Live at https://f1.chinnaboina.com/ AND https://Deltasthic-f1-strategist.hf.space/

## Phase 8 — HF Space ✅
- Deployed via `huggingface_hub.upload_folder()` (bypasses git-lfs need for binaries)
- W2 hackathon requirement satisfied
- Updated `demo-assets/hf-space-link.txt` with all three live URLs

## Merge details — origin/main → dev (commit d763d0b)
- Pulled trained checkpoint (~10 checkpoints × LoRA adapter + tokenizer files)
- Resolved 1 conflict in train.py
- Auto-merged .gitignore additions
- 164 tests still passing post-merge
