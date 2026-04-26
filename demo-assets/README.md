# demo-assets/

Static artefacts linked from the README and the HF Space landing page.

## Contents

| File | What |
|---|---|
| `blog-post.md` | Optional blog draft |
| `hf-space-link.txt` | Live Space URL |
| `hf-blog-link.txt` | Link to `blog.md` on the Space |
| `youtube-link.txt` | Not used (blog + Colab are the demo deliverables) |
| `submission-confirmation.png` | After form submit (optional) |
| `*.gif` | Before/after rollouts |

## Workflow

1. Generate GIFs with `python rollout.py` or `scripts/run_full_demo.py`, then place GIFs here.
2. Publish the Space; save the URL in `hf-space-link.txt`.
3. Point `hf-blog-link.txt` at `https://huggingface.co/spaces/Deltasthic/f1-strategist/blob/main/blog.md`.
