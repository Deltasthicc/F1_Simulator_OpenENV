# SUBMISSION RUNBOOK — Final, Comprehensive Checklist

**Deadline:** 26 April 5 PM IST. Last commit before this matters; nothing after.

**Team decision (submission):** No YouTube video. Demo deliverables are **blog (`blog.md`) + Colab notebook + live Space** only. Skip **Section 6** (video) entirely.

This is your ONE document. Walk it top-to-bottom. Every required step is here. Every artifact, every command, every URL.

**Hard stop:** If the clock hits **4:00 PM IST and you haven't finished Section 7**, jump straight to Section 9 (Emergency fallback). The submission form takes ~2 minutes; preserve that buffer.

---

## Quick map

| Section | What it does | Estimated time |
|---|---|---|
| 0 | Save artifacts, save form draft, verify what's already live | 10 min |
| 1 | Merge partner's `dev` branch into `main` | 15 min |
| 2 | Sync all docs from the new eval JSON | 5 min |
| 3 | Install the live track simulator on the landing page | 15 min |
| 4 | Re-render before/after GIFs (only if model behavior changed) | 10 min via SSH |
| 5 | Check the model card on HF Hub | 2 min |
| 6 | *(Skipped — no video; blog + Colab + Space only)* | — |
| 7 | Final pre-push checklist (10-step) | 15 min |
| 8 | Tag + final push + submit | 5 min |
| 9 | Emergency fallback (if partner can't fix in time) | 20 min |

**Total best case: ~2 hours** with no video work.

---

## 0. Pre-prep — do this immediately

### 0.1 Save the eight artifact files

You have eight files from chat. Place them as follows:

| File | Destination |
|---|---|
| `blog.md` | `blog.md` (project root, replaces existing) |
| `f1_strategist_training_colab.ipynb` | `notebooks/f1_strategist_training_colab.ipynb` (replaces existing) |
| `sync_results_to_docs.py` | `scripts/sync_results_to_docs.py` |
| `push_to_space.py` | `push_to_space.py` (project root) |
| `track-map.js` | `server/static/track-map.js` (NEW file) |
| `simulator-integration.md` | `simulator-integration.md` (project root, reference doc) |
| `SUBMISSION_RUNBOOK.md` | `SUBMISSION_RUNBOOK.md` (this file) |

### 0.2 Confirm what's already live and locked

Open in **incognito browser**:

- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist` — landing page loads, status "Running"
- [ ] `https://huggingface.co/Deltasthic/f1-strategist-qwen3-4b-grpo` — model card public, weights listed
- [ ] Live smoke test:
  ```powershell
  python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space
  ```
  Should print "All 6 checks passed" (includes non-empty `/readme` for the playground sidebar).

### 0.3 Pre-fill the submission form (save draft, don't submit)

| Field | Value |
|---|---|
| Email | `shashwat.rajan2005@gmail.com` |
| HF Space URL | `https://huggingface.co/spaces/Deltasthic/f1-strategist` |
| Training Run Notebook URL | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/notebooks/f1_strategist_training_colab.ipynb` |
| Demo type | **Blog Post** only (no video) |
| Blog URL | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/blog.md` |

Save draft.

---

## 1. Merge partner's `dev` branch into `main`

Your partner pushed his model fix and corrected eval to a `dev` branch. You're on `main`. The merge brings his work over. Conflicts are expected.

### 1.1 Fetch and inspect

```powershell
cd C:\Users\shash\Downloads\F1_RL_Simulator\Project
git fetch origin
git log --oneline origin/dev -10
git log --oneline origin/main -10
git diff main..origin/dev --stat
```

The `--stat` line shows you which files differ. Mentally categorize each:

| File pattern | Whose version to keep |
|---|---|
| `evaluate.py`, `inference.py`, `server/*.py` (new code paths) | **Partner's (dev)** — these contain the LoRA-load fix |
| `results/eval_summary.json` | **Partner's (dev)** — honest numbers |
| `results/eval_curve.png`, `results/training_loss_curve.png` | **Partner's (dev)** — fresh plots |
| `grpo_v1/**` (model checkpoints) | **Partner's (dev)** — but these are gitignored anyway |
| `README.md`, `blog.md`, `notebooks/*.ipynb` | **Yours (main)** — contains marker structure + cleaner narrative |
| `.gitignore`, `requirements.lock`, `pyproject.toml` | Whichever is newer; usually safe to take partner's |
| `demo-assets/*.gif` | Partner's only if he re-rendered them |

### 1.2 Pull dev into main

```powershell
git checkout main
git pull origin main
git merge origin/dev --no-commit --no-ff
```

The `--no-commit` flag stops the merge before it's finalised, so you can resolve conflicts cleanly.

### 1.3 Resolve conflicts file by file

Run `git status` to see unmerged files. For each:

```powershell
# Take partner's version (his fix)
git checkout --theirs evaluate.py inference.py
git checkout --theirs results/eval_summary.json results/eval_curve.png
git checkout --theirs results/training_loss_curve.png

# Keep your version (markers, narrative)
git checkout --ours blog.md README.md
git checkout --ours notebooks/f1_strategist_training_colab.ipynb

# server/*.py — take partner's if his changes are about model loading or scoring
git checkout --theirs server/environment.py server/scoring.py
# But if he didn't touch them, this is a no-op

# Anything else — open in editor and pick line by line
```

If any file is stuck after this, open it in VS Code or Notepad++. You'll see `<<<<<<< HEAD ... ======= ... >>>>>>> dev` markers. For each conflict block:

- If it's about code logic (model loading, eval, training) → keep partner's (between `=======` and `>>>>>>>`)
- If it's about narrative/numbers/markdown → keep yours (between `<<<<<<<` and `=======`)
- Save, then `git add <file>`

### 1.4 Verify the merge isn't broken

```powershell
git status
# Should show no unmerged paths
```

Run a quick sanity check on the critical files:

```powershell
# Confirm partner's eval JSON arrived with new numbers
python -c "import json; d=json.load(open('results/eval_summary.json')); [print(f'{m:<10}', {t: round(d[m][t]['mean'],3) for t in d[m]}) for m in d]"
```

Trained means must differ from `0.749 / 0.935 / 0.935 / 0.535` (those were the bullshit fallback values). If they're identical, the merge took your old JSON instead of partner's — re-run `git checkout --theirs results/eval_summary.json`.

```powershell
# Confirm your blog still has marker structure
findstr /C:"AUTO_UPDATE_START" blog.md
# Should print 3 marker lines
```

If `findstr` returns nothing, your `blog.md` got overwritten — restore from `/mnt/user-data/outputs/blog.md`.

### 1.5 Commit the merge

```powershell
git commit -m "merge: dev into main — partner's honest eval + LoRA-load fix; keep main's narrative blog"
git push origin main
```

---

## 2. Sync all docs from the new eval JSON

```powershell
python scripts\sync_results_to_docs.py
```

Expected output:

```
Source of truth: ...\results\eval_summary.json
Trained means:
  dry_strategy_sprint   u=0.XXX  t=0.XXX  e=0.XXX  Δ=+0.XXX  gap_closed=XX%
  weather_roulette      u=0.XXX  t=0.XXX  e=0.XXX  Δ=+0.XXX  gap_closed=XX%
  ...

[README] updated results table
[blog]   updated marker blocks (results_table, weather_headline, keydecision_delta)
[ipynb]  updated summary markdown cells
```

If `[blog]` says "ERROR: blog.md is missing or too short", restore it from artifacts.

If `[blog]` says "WARN: markers found but nothing matched", the marker names in your blog don't match the script — check that the marker names are exactly `results_table`, `weather_headline`, `keydecision_delta`.

### 2.1 Spot-check the sync worked

```powershell
findstr /A:F /C:"GRPO trained" README.md
findstr /A:F /C:"AUTO_UPDATE_START" blog.md
findstr /A:F /C:"GRPO closes" notebooks\f1_strategist_training_colab.ipynb
```

Open each file briefly in your editor. The numbers in the tables should match the partner's new JSON.

### 2.2 Commit the sync

```powershell
git add results/ README.md blog.md notebooks/ demo-assets/
git commit -m "docs: sync all narrative artifacts to honest eval numbers"
git push origin main
```

---

## 3. Install the live track simulator on the landing page

This is the visual upgrade — adds an animated track map next to the decision log. Drop-in, doesn't break anything if you do the patches correctly.

### 3.1 Add the track-map.js file

You should have already saved `track-map.js` to `server/static/track-map.js` in step 0.1.

### 3.2 Apply the three patches

Open `simulator-integration.md` and follow the three patches exactly:

1. **Patch 2** — `server/static/index.html`: add the `<script>` tag, wrap the lap log in a 2-column body
2. **Patch 3** — `server/static/app.js`: three small additions inside `setupSimWidget()`

The patches are surgical — each is 2-5 lines.

### 3.3 Verify locally if you can run the server

```powershell
python -m server.app
# Open http://localhost:8000/ in your browser
# Scroll to "TRY IT LIVE" section
# Click RUN RACE
```

You should see the decision log on the left **and** the track map with a red car circling on the right.

If the track doesn't appear, open devtools console and check:
- `window.TrackMap` should not be `undefined` (means script loaded)
- Any red error messages — paste me the first one

If you can't run the server locally, just push and check on the deployed Space.

### 3.4 Commit and push the simulator

```powershell
git add server/static/track-map.js server/static/index.html server/static/app.js
git commit -m "feat: add animated track map alongside decision log in race simulator"
git push origin main
```

### 3.5 Push to HF Space

```powershell
$env:HF_TOKEN = "PASTE_FRESH_TOKEN"
python push_to_space.py "feat: live track map + honest eval"
```

Wait ~3 min for rebuild, then verify on the live URL:

```powershell
python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space
```

Open `https://Deltasthic-f1-strategist.hf.space` in incognito. Click RUN RACE. The track map should appear and animate.

If it doesn't appear on the live site but the smoke test passes:
- Build log might have a JS syntax error from a typo in the HTML patch
- Open browser devtools (F12) → Console tab on the live URL → look for red errors
- Most common fix: verify the `<svg id="track-svg">` and the script tag are both present in the page source

---

## 4. Re-render before/after GIFs (optional)

Only do this if your partner says the trained model behavior is **materially different** from the old GIFs. If the trained model still calls REQUEST_FORECAST early and pits for inters at lap 7-8 on weather_roulette seed 7, the existing GIFs are fine — skip this section.

If behavior changed, only the GPU server has the real weights:

```bash
ssh server
cd F1_Simulator_OpenENV && source .venv/bin/activate && git pull origin main
python rollout.py --task weather_roulette --seed 7 --mode untrained --render --verbose
python rollout.py --task weather_roulette --seed 7 --mode trained --model grpo_v1/checkpoint-500 --render --verbose
mv captures/weather_roulette_untrained_seed7.gif demo-assets/untrained-spa.gif
mv captures/weather_roulette_trained_seed7.gif   demo-assets/trained-spa.gif
git add demo-assets/ && git commit -m "regen GIFs from corrected model" && git push origin main
exit
```

Then on Windows:

```powershell
git pull origin main
python push_to_space.py "regen GIFs"
```

Also save the new transcript:

```bash
# On the server, after the rollouts above
cat captures/weather_roulette_trained_seed7.jsonl | head -20 > demo-assets/trained-rollout-transcript.txt
git add demo-assets/trained-rollout-transcript.txt && git commit -m "transcript" && git push origin main
```

---

## 5. Verify the model card on HF Hub

You said this is done. Quick verification:

Open `https://huggingface.co/Deltasthic/f1-strategist-qwen3-4b-grpo` in incognito. Confirm:

- [ ] Page loads
- [ ] Has a real description (not just file list)
- [ ] License visible (MIT)
- [ ] `library_name: peft` in metadata
- [ ] Tags: `grpo`, `openenv`, `formula-one`, `lora`, `qwen` or similar
- [ ] `adapter_model.safetensors` (132 MB) listed in Files
- [ ] Repo is **public** (no "gated" or "private" badge)

If any of those is missing, click "Edit model card" and patch it now. 5-minute fix.

---

## 6. Video (out of scope for this submission)

**Do not** record, upload, or link a YouTube (or any) demo video. The team is submitting **Blog post** on the form: `blog.md` on the Space, plus the Colab notebook and live Space. Leave any video field empty; do not add `demo-assets/youtube-link.txt` beyond the existing “not used” placeholder.

---

## 7. Final pre-push checklist — walk in order, do not skip

### 7.1 Repository hygiene

- [ ] `git status` is clean
- [ ] No secrets in history:
  ```powershell
  git log -p | findstr /R "hf_[a-zA-Z0-9]" | findstr /V "f1-strategist"
  ```
  Should print nothing.
- [ ] No accidentally-committed huge files:
  ```powershell
  git ls-files | ForEach-Object { (Get-Item $_).Length, $_ } | Sort-Object | Select-Object -Last 10
  ```
  Anything > 10 MB should be gitignored.
- [ ] `.gitignore` includes: `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `captures/*.gif`, `captures/*.mp4`, `grpo_*/checkpoint-*/`

### 7.2 README accuracy

- [ ] HF Space frontmatter (YAML at top) intact: `title`, `emoji`, `sdk: docker`, `app_port: 8000`
- [ ] Notebook URL points to **HF Space**, not private GitHub
- [ ] Blog URL points to `blog.md` on HF Space
- [ ] No demo video linked (blog-only; README has no YouTube line)
- [ ] All `results/*.png` referenced actually exist
- [ ] Trained numbers in README match `results/eval_summary.json` (run sync if not)

### 7.3 Phase 1 (Environment) gating

- [ ] `python -m server.app` starts without errors
- [ ] `python tests\smoke_http.py` passes 6/6 locally
- [ ] `python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space` passes 6/6 against live Space
- [ ] `python -m pytest tests/ -q` — all tests pass

### 7.4 Phase 2 (Scenarios + Scoring)

- [ ] `python tests\smoke_all_scenarios.py` — expert ≥ 0.85, panic ≤ 0.40 each family
- [ ] Expert traces exist in `baselines/trajectories/`

### 7.5 Phase 3 (Training) — CRITICAL

- [ ] `results/training_loss_curve.png` exists, real GRPO curve (not the smoke fallback)
- [ ] `results/eval_summary.json` has all four modes × four tasks
- [ ] `results/eval_curve.png` shows trained ≥ untrained + 0.10 average minimum
- [ ] `Deltasthic/f1-strategist-qwen3-4b-grpo` is public on HF Hub with real adapter_model.safetensors

### 7.6 Phase 4 (Self-improvement)

- [ ] `server/postmortem.py` records postmortems on episode end
- [ ] `reset()` injects `memory_hints` from past postmortems
- [ ] `results/ablation.md` claims a positive memory delta only if positive

### 7.7 Phase 5 (Demo + Deploy)

- [ ] HF Space status: **Running**
- [ ] Live smoke test passes
- [ ] Track map renders on the live page (open in incognito, click RUN RACE)
- [ ] Before/after GIFs in `demo-assets/`
- [ ] `demo-assets/trained-rollout-transcript.txt` exists
- [ ] `demo-assets/youtube-link.txt` remains the “not used” placeholder (no video)

### 7.8 Submission requirements W1–W4

- [ ] **W1** — `pip show openenv-core` shows ≥ 0.2.3
- [ ] **W1** — Notebook committed and runnable from HF Space
- [ ] **W2** — HF Space exists, public, Running
- [ ] **W3** — Blog at HF Space `blog.md` URL (demo type: Blog post)
- [ ] **W4** — README links: HF Space, Notebook, blog, eval_curve.png, training_loss_curve.png, model weights (no video)

### 7.9 Theme alignment

- [ ] README "Theme alignment" section references Theme #2 (Long-Horizon) + #3.1 (Professional Tasks)
- [ ] Blog opens by motivating long-horizon planning (the "Lap 8" hook)

### 7.10 Final smoke

```powershell
python tests\smoke_http.py
python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space

@(
  "results\eval_summary.json",
  "results\eval_curve.png",
  "results\training_loss_curve.png",
  "blog.md",
  "demo-assets\hf-space-link.txt",
  "demo-assets\untrained-spa.gif",
  "demo-assets\trained-spa.gif",
  "notebooks\f1_strategist_training_colab.ipynb",
  "server\static\track-map.js"
) | ForEach-Object {
  if (Test-Path $_) { Write-Host "  ok: $_" } else { Write-Host "  MISSING: $_" -ForegroundColor Red }
}
```

If anything reports `MISSING`, fix it before tagging.

---

## 8. Tag, final push, submit

### 8.1 Tag the submission

```powershell
git tag -a v1.0-finale -m "Meta PyTorch OpenEnv Hackathon Grand Finale submission"
git push origin main --tags
```

### 8.2 Final push to HF Space

```powershell
python push_to_space.py "v1.0-finale tag"
```

Wait ~3 min for rebuild. Re-smoke:

```powershell
python tests\smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space
```

### 8.3 Final incognito verification

Open all six URLs in incognito. Each must load:

- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist`
- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/blog.md`
- [ ] `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/notebooks/f1_strategist_training_colab.ipynb`
- [ ] `https://huggingface.co/Deltasthic/f1-strategist-qwen3-4b-grpo`
- [ ] (If applicable) GitHub repo URL

### 8.4 Submit the form

Open the saved form draft. Verify all four URL fields have current values. Click **Submit**.

Screenshot the confirmation page. Save as `demo-assets/submission-confirmation.png`.

```powershell
git add demo-assets/submission-confirmation.png
git commit -m "submission: confirmation screenshot"
git push origin main
```

---

## 9. Emergency fallback

Trigger this if **at 4:00 PM IST** the partner hasn't pushed his fix or the merge is unworkable.

### 9.1 Edit `blog.md` to be honest

Find the Results section. Replace the table content between the markers with:

```
| Scenario | Random | Untrained | Trained (in progress) | Expert |
|---|---:|---:|---:|---:|
| Dry strategy sprint | 0.40 | 0.51 | _pending_ | 0.84 |
| Weather roulette | 0.34 | 0.41 | _pending_ | 0.95 |
| Late safety car | 0.33 | 0.53 | _pending_ | 0.94 |
| Championship decider | 0.21 | 0.27 | _pending_ | 0.97 |
```

Find the headline sentence between markers. Replace with:

```
The trained model demonstrates the investigation-then-action pattern (REQUEST_FORECAST → INSPECT_TYRE_DEGRADATION → RADIO_DRIVER → PIT_NOW inter) on Spa weather scenario, scoring 0.95 vs 0.38 untrained on a single seed. Multi-seed evaluation against the corrected LoRA-load path is in progress at submission time.
```

Find the keydecision delta between markers. Replace with:

```
Trained score on the highlighted seed: **0.950** vs **0.378** untrained.
```

Save. Don't run the sync script (it would overwrite these manual edits).

### 9.2 Quick commit + push

```powershell
git add blog.md
git commit -m "fallback: honest interim blog (multi-seed eval pending)"
git push origin main
python push_to_space.py "fallback: honest interim blog"
```

### 9.3 Submit before 5 PM

Use the blog URL as the demo deliverable (Blog post on the form).

**Honest narrative + working environment + evidence of training + valid notebook > polished narrative + missed deadline.** Submit.

---

## 10. Post-deadline cleanup (after submission)

- Rotate the HF token you pasted in chat: https://huggingface.co/settings/tokens → invalidate `F1-Simulator` → create new write token.
- Make GitHub repo public if you intend to share the source code, OR update README to declare HF Space the canonical source.
- Take notes on what could've been smoother: pin the eval verifier sooner, separate model-load path from scripted fallback at the API level, set up CI on env tests.

---

## URL reference card (paste-ready for the form)

| Field | URL |
|---|---|
| HF Space | `https://huggingface.co/spaces/Deltasthic/f1-strategist` |
| Notebook | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/notebooks/f1_strategist_training_colab.ipynb` |
| Blog (default) | `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/blog.md` |
| Trained model | `https://huggingface.co/Deltasthic/f1-strategist-qwen3-4b-grpo` |

---

Good luck. You've earned this submission the hard way. Don't blow it on the last mile.