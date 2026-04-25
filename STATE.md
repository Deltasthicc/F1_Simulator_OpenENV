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
- [ ] Phase 4 — Generate SFT seed data
- [ ] Phase 5 — GRPO smoke run (50 steps, Qwen3-0.6B)
- [ ] Phase 6 — Full GRPO (500 steps, Qwen3-4B) — runs ~4h
- [ ] Phase 7 — Landing page + Gradio polish (parallel with 6)
- [ ] Phase 8 — Push checkpoint to HF Hub [BLOCKED on HF_TOKEN]
- [ ] Phase 9 — Eval against trained checkpoint
- [ ] Phase 10 — Demo polish (GIFs, blog, video)
- [ ] Phase 11 — Pre-push checklist + tag v1.0-finale
- [ ] Phase 12 — Storytelling extras (historical replay, leaderboard)

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
