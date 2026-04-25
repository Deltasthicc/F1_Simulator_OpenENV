# Video Script — F1 Strategist demo

> Target runtime: ≤ 1:50 (under the 2:00 W3 minimum).
> Format: screen capture of visualizer GIFs + eval bar chart + a few code snippets.
> Voice-over by Shashwat or Tanish, recorded in OBS or QuickTime.
> Final upload: YouTube unlisted-or-public, link saved to `demo-assets/youtube-link.txt`.

---

## Storyboard

### Beat 1 — Title (0:00–0:08)

**Visual:** Black title card. White type. F1 Strategist logo (or just typography).
**On-screen text:**
```
F1 Strategist
Train an LLM to call F1 race strategy
```
**Voice:** *"Can you train a language model to call Formula 1 race strategy?"*

---

### Beat 2 — Untrained agent fails (0:08–0:35)

**Visual:** Visualizer GIF, weather roulette at Spa, untrained Qwen3-4B running. Top-down track view, ego car circle, opponents around it. Lap counter ticks 1 → 12. Around lap 6, rain ramps up (visualized as a blue overlay on the track). The untrained agent stays out. Lap times balloon. Position drops from P5 to P9. Final score 0.30 lands on screen.

**Voice:** *"Untrained, our model stays out as the rain hits Spa. Lap times balloon. We drop four positions. The final score is 0.30."*

**On-screen text** (at end of clip):
```
Untrained Qwen3-4B
Score: 0.30
Decisions: STAY_OUT, STAY_OUT, STAY_OUT…
```

---

### Beat 3 — Trained agent succeeds (0:35–1:05)

**Visual:** Same scenario, same seed, the *trained* agent. The agent issues `REQUEST_FORECAST` at lap 5 — overlay shows the rain probability cone appearing. At lap 7, the agent calls `PIT_NOW inter` one lap before the rain peak. Smooth lap times follow. Cars on slicks behind it visibly slide and lose pace. Final position P2, score 0.91.

**Voice:** *"Trained, the same model calls for the forecast at lap 5. Inspects the tyres. Boxes for inters one lap before the rain peak. P2 finish. Score 0.91. Same seed, same opponents — different decisions."*

**On-screen text:**
```
Trained Qwen3-4B (500 GRPO steps)
Score: 0.91
Decisions: REQUEST_FORECAST, INSPECT_TYRE_DEGRADATION, PIT_NOW inter…
```

---

### Beat 4 — The numbers (1:05–1:30)

**Visual:** `results/eval_curve.png` — the four-bar grouped chart, one cluster per scenario family, four bars per cluster (random / untrained / trained / expert). Trained bars sit clearly between untrained and expert. Animate the trained bars rising into place.

**Voice:** *"Across four scenario families and five held-out seeds, the trained policy improves by 30 points on average over the untrained baseline. Half the gap to the rule-based expert, after 500 GRPO steps on a single RTX 5090."*

**On-screen text:**
```
+0.30 average
500 GRPO steps · 1× RTX 5090 · Qwen3-4B + LoRA
```

---

### Beat 5 — How it works (1:30–1:45)

**Visual:** Quick cuts:
- A few lines of the action grammar from `inference.py` SYSTEM_PROMPT
- The six-dimension scoring formula from `docs/reward-model.md`
- A flash of a postmortem JSON entry

**Voice:** *"Six-dimension deterministic scoring, 20 strategic commands, hidden state revealed by inspection, postmortem memory across episodes. Built on OpenEnv. All open source."*

---

### Beat 6 — Call to action (1:45–1:50)

**Visual:** End card with three QR codes / URLs.
**On-screen text:**
```
🌐 huggingface.co/spaces/Deltasthic/f1-strategist
📝 Blog: [hf-blog-link]
💻 github.com/Deltasthicc/f1-strategist

Meta PyTorch OpenEnv Hackathon Grand Finale 2026
Shashwat Rajan · Tanish Shitanshu · Deltasthic
```
**Voice:** *"Try it yourself. Hugging Face Space, code, blog post linked below."*

---

## Recording notes

- **Audio:** USB condenser or AirPods Pro mic. Quiet room. One take per beat,
  splice together.
- **Captions:** YouTube auto-captions are usually 80% right; manually fix the
  technical terms (Qwen3, GRPO, undercut, RL).
- **Music:** None. Voice-over only. Race-strategy content reads as serious.
- **Aspect ratio:** 16:9, 1080p minimum.
- **Render:** OBS local recording → minor cuts in DaVinci Resolve free → export.
  No after-effects needed; the GIFs do the work.

## Asset inventory needed before recording

- [ ] `demo-assets/untrained-spa.gif` — 25-second visualizer GIF (Person 1)
- [ ] `demo-assets/trained-spa.gif` — 25-second visualizer GIF (Person 1)
- [ ] `results/eval_curve.png` — final bar chart (Person 2)
- [ ] Side-by-side composite of the two GIFs, if practical (optional)
- [ ] End-card PNG with the three URLs filled in (post-deploy)

If any asset isn't ready, cut that beat and adjust runtime to keep < 2:00.
