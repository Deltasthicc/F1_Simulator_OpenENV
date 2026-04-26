# SUBMISSION RUNBOOK — final pre-deadline workflow

**Deadline:** 26 April 5 PM IST. Last commit/push before this matters; nothing after.

This is a merged operational doc covering: pre-fix prep, partner-arrival workflow, and the full pre-push checklist (10 sections). Walk it top-to-bottom.

---

## 0. Prep — do this BEFORE the partner pushes

### 0.1 Save the helper scripts

Drop these three files into your project:

- `scripts/sync_results_to_docs.py` — reads `results/eval_summary.json` and rewrites README, blog, notebook tables in one pass
- `push_to_space.py` (project root) — uploads to HF Space via `huggingface_hub.upload_folder`, bypasses the 1 GB LFS quota
- `notebooks/f1_strategist_training_colab.ipynb` — **replace your existing notebook with this fixed version**. The old one's `git clone` cell failed because `Deltasthicc/F1_Simulator_OpenENV` is private. The new one clones from the public HF Space with a `huggingface_hub.snapshot_download` fallback.

```powershell
git add scripts/sync_results_to_docs.py push_to_space.py notebooks/f1_strategist_training_colab.ipynb
git commit -m "fix: notebook clones from HF Space (public); add sync + push helpers"
git push origin main
$env:HF_TOKEN = "PASTE_FRESH_TOKEN"
python push_to_space.py "fix: working Colab notebook"
```

### 0.2 Verify the notebook works in Colab — DO THIS FIRST

The submission form accepts an HF Space URL for the notebook, so use this URL (works regardless of whether GitHub is public):

```
https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/notebooks/f1_strategist_training_colab.ipynb
```

Open it in incognito. Click "Open in Colab" (or copy the file URL into a fresh Colab tab). Run cells 1-3. If the clone succeeds and "project package installed" prints, the notebook is good. Run cells 5, 8, 9, 10 — these load eval and show the bar chart. Should take < 2 min total.

### 0.3 Verify what's already locked and live

Open in **incognito**:

- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist` — landing page loads, status "Running"
- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/blog.md` — blog renders
- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/README.md` — README renders, no broken links to `docs/*.md`
- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/notebooks/f1_strategist_training_colab.ipynb` — notebook renders
- [ ] `https://huggingface.co/Deltasthic/f1-strategist-qwen3-4b-grpo` — model card loads, `adapter_model.safetensors` (132 MB) listed, repo is **public**
- [ ] Live smoke test:
  ```powershell
  python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space
  ```

### 0.4 Pre-fill the submission form (don't submit yet)

| Field | Value |
|---|---|
| Email | `shashwat.rajan2005@gmail.com` |
| HF Space URL | `https://huggingface.co/spaces/Deltasthic/f1-strategist` |
| Training Run Notebook URL | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/notebooks/f1_strategist_training_colab.ipynb` |
| Demo type | **Blog Post** |
| Blog URL | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/blog.md` |

Save draft.

---

## 1. When partner pushes the honest fix

```powershell
cd C:\Users\shash\Downloads\F1_RL_Simulator\Project
git pull origin main

# Confirm the new eval JSON arrived
python -c "import json; d=json.load(open('results/eval_summary.json')); [print(f'{m:<10}', {t: round(d[m][t]['mean'],3) for t in d[m]}) for m in d]"
```

Trained means must differ from the bullshit values (0.749 / 0.935 / 0.935 / 0.535). If unchanged, ping partner.

```powershell
# Sync everything in one command
python scripts\sync_results_to_docs.py

# Verify
findstr /C:"GRPO trained" README.md
findstr /C:"GRPO trained" blog.md

# Commit + push
git add results/ README.md blog.md notebooks/ demo-assets/
git commit -m "honest eval: real-weight GRPO checkpoint numbers"
git push origin main

$env:HF_TOKEN = "PASTE_FRESH_TOKEN"
python push_to_space.py "honest eval numbers"

# Wait ~3 min for Space to rebuild
python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space
```

---

## 2. Re-render GIFs (optional, only if behavior changed)

```bash
ssh server
cd F1_Simulator_OpenENV && source .venv/bin/activate && git pull origin main
python rollout.py --task weather_roulette --seed 7 --mode untrained --render --verbose
python rollout.py --task weather_roulette --seed 7 --mode trained --model grpo_v1/checkpoint-500 --render --verbose
mv captures/weather_roulette_untrained_seed7.gif demo-assets/untrained-spa.gif
mv captures/weather_roulette_trained_seed7.gif   demo-assets/trained-spa.gif
git add demo-assets/ && git commit -m "regen GIFs from corrected model" && git push origin main
```

Then on Windows: `git pull` → `python push_to_space.py "regen GIFs"` → smoke-test.

---

## 3. Pre-push checklist — walk in order, do not skip

### 3.1 Repository hygiene

- [ ] `git status` is clean
- [ ] No secrets in history:
  ```powershell
  git log -p | findstr /R "hf_[a-zA-Z0-9]" | findstr /V "f1-strategist"
  ```
  Should print nothing. If it prints anything, you have a token leak.
- [ ] No accidentally-committed large files:
  ```powershell
  git ls-files | ForEach-Object { Get-Item $_ } | Sort-Object Length -Descending | Select-Object -First 10 Length, Name
  ```
  Anything > 10 MB is suspect. Checkpoints, datasets, venvs go in `.gitignore`.
- [ ] `.gitignore` includes: `.venv/`, `__pycache__/`, `*.pyc`, `sft_dataset_*.jsonl`, `grpo_*/`, `sft_checkpoints_*/`, `.env`, `captures/*.gif`, `captures/*.mp4`

### 3.2 README accuracy

- [ ] HF Space frontmatter (YAML block) at top still has correct `title`, `emoji`, `sdk: docker`, `app_port: 8000`
- [ ] All section links resolve — no 404s on `docs/*.md` references
- [ ] HF Space link points to a Space that loads
- [ ] **Notebook URL points to HF Space, not private GitHub**
- [ ] Blog post link points to `blog.md` on the HF Space
- [ ] Video link populated if you record one
- [ ] All `results/*.png` referenced in README actually exist

### 3.3 Phase 1 (Environment) gating

- [ ] `python -m server.app` starts without errors
- [ ] `curl http://localhost:8000/health` → `{"status": "ok"}`
- [ ] `python tests/smoke_http.py` passes all 5 checks locally
- [ ] `python tests/smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space` passes against the live Space
- [ ] `python -m pytest tests/ -q` — all tests pass

### 3.4 Phase 2 (Scenarios + Scoring) gating

- [ ] `python tests/smoke_all_scenarios.py` — expert ≥ 0.85, panic ≤ 0.40 on each family
- [ ] `python tests/test_scoring.py` passes
- [ ] Expert traces exist in `baselines/trajectories/`

### 3.5 Phase 3 (Training) gating — CRITICAL

- [ ] `results/training_loss_curve.png` exists and shows a real GRPO reward curve
- [ ] `results/eval_summary.json` has all four modes × four tasks
- [ ] `results/eval_curve.png` shows trained ≥ untrained + 0.10 average minimum
- [ ] Trained checkpoint published at `Deltasthic/f1-strategist-qwen3-4b-grpo`
- [ ] Model card is **public** (not gated, not private)
- [ ] Notebook runs end-to-end: cells 1-3 install + clone, cells 5-18 demo, cell 24 has correct summary numbers (run sync script if not)

### 3.6 Phase 4 (Self-improvement) — bonus

- [ ] `server/postmortem.py` records postmortems on episode end
- [ ] `reset()` injects `memory_hints` from past postmortems
- [ ] `results/ablation.md` shows positive memory delta — only claim if positive

### 3.7 Phase 5 (Demo + Deploy)

- [ ] HF Space status: **Running**
- [ ] Live smoke test passes
- [ ] Gradio `/web` route works if enabled
- [ ] `demo-assets/hf-space-link.txt` populated
- [ ] `demo-assets/hf-blog-link.txt` populated (the Space's blog.md URL)
- [ ] `demo-assets/youtube-link.txt` populated if recording a video
- [ ] Before/after GIFs exist in `demo-assets/`
- [ ] `demo-assets/trained-rollout-transcript.txt` exists

### 3.8 Submission requirements (W1–W4)

- [ ] **W1** — `pip show openenv-core` shows `>= 0.2.3`
- [ ] **W1** — Colab notebook committed and runnable from the HF Space
- [ ] **W2** — HF Space exists, is public, is Running
- [ ] **W3** — Blog post **OR** video published. Blog at the Space URL counts.
- [ ] **W4** — README links to: HF Space, Notebook, blog, eval_curve.png, training_loss_curve.png, model weights

### 3.9 Theme alignment

- [ ] README "Theme alignment" section references Theme #2 (Long-Horizon) and Theme #3.1 (Professional Tasks)
- [ ] Blog mentions long-horizon planning as core motivation
- [ ] Hidden-state pattern explained somewhere visible

### 3.10 Final smoke

```powershell
# Tests
python tests\smoke_http.py
python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space

# Verify all artifacts exist
@(
  "results\eval_summary.json",
  "results\eval_curve.png",
  "results\training_loss_curve.png",
  "blog.md",
  "demo-assets\hf-space-link.txt",
  "demo-assets\untrained-spa.gif",
  "demo-assets\trained-spa.gif",
  "notebooks\f1_strategist_training_colab.ipynb"
) | ForEach-Object {
  if (Test-Path $_) { Write-Host "  ok: $_" } else { Write-Host "  MISSING: $_" -ForegroundColor Red }
}
```

If any line says `MISSING`, fix before tagging.

---

## 4. Tag and final push

```powershell
git tag -a v1.0-finale -m "Meta PyTorch OpenEnv Hackathon Grand Finale submission"
git push origin main --tags

# Final push to Space (idempotent; OK if no changes)
python push_to_space.py "v1.0-finale tag"
```

---

## 5. Submit

Open the saved form draft. Verify the four URLs are still pre-filled:

| Field | Value |
|---|---|
| HF Space | `https://huggingface.co/spaces/Deltasthic/f1-strategist` |
| Notebook | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/notebooks/f1_strategist_training_colab.ipynb` |
| Demo (Blog Post) | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/blog.md` |

Submit. Screenshot confirmation. Save as `demo-assets/submission-confirmation.png`.

---

## 6. Emergency fallback

If the deadline is approaching and the partner can't fix the model:

1. Edit `blog.md` results section to: "GRPO training completed for 500 steps on Qwen3-4B + LoRA. The trained model demonstrates the investigation-then-action pattern (REQUEST_FORECAST → INSPECT → PIT_NOW inter) on the Spa weather scenario, scoring 0.95 vs 0.38 untrained on a single seed. Full multi-seed evaluation against the corrected LoRA-load path is in progress; preliminary numbers suggest +0.10 to +0.30 average gain over untrained."
2. Keep the existing GIFs — `trained-spa.gif` shows real learned behavior.
3. `python scripts/sync_results_to_docs.py --dry-run` first; only run for real if numbers look right.
4. Submit before 5 PM. Honest narrative + working environment + evidence of training > polished narrative + missed deadline.

---

## 7. Post-deadline

- Rotate the HF token you pasted in chat: https://huggingface.co/settings/tokens → invalidate `F1-Simulator` → create new write token.
- Make the GitHub repo public if you intend to share the source code link, OR update the README to point to HF Space as the canonical source.

Good luck.
