"""
F1 Strategist — TRL GRPO Training
===================================

Multi-turn GRPO with the OpenEnv environment_factory pattern. Mirrors the
OpsTwin V3 training script shape, tuned for the F1 env.

Owner: Person 2 (Tanish).
Spec: TRAINING.md, GPU_HANDOFF.md.

TODO Phase 3:
    - GRPOConfig (model, max_steps, batch, grad_accum, save_steps, output_dir)
    - environment_factory: returns a fresh F1StrategistEnv per rollout worker
    - tokenizer setup with Qwen3 chat template
    - Unsloth wrapper for the 4B + LoRA path on the 5090
    - argparse: --model, --task, --max-steps, --batch-size, --grad-accum,
        --warm-start-sft, --reward-mode (shaped|sparse), --output-dir
    - tee training_log.txt during run

CLI:
    # Smoke
    python train.py --model Qwen/Qwen3-0.6B --max-steps 50 --batch-size 1 --grad-accum 8

    # Full
    python train.py --model Qwen/Qwen3-4B --max-steps 500 --batch-size 1 --grad-accum 32 \\
        --warm-start-sft ./sft_checkpoints_v1/checkpoint-200 \\
        --output-dir ./grpo_v1
"""
import argparse


def make_env_factory(task: str):
    """Returns a callable that constructs a fresh F1StrategistEnv per worker."""
    raise NotImplementedError("Phase 3, Person 2")


def main(args):
    raise NotImplementedError("Phase 3, Person 2")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-4B")
    parser.add_argument("--task", default="multi", help="single task or 'multi'")
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=32)
    parser.add_argument("--warm-start-sft", default=None)
    parser.add_argument("--reward-mode", choices=["shaped", "sparse"], default="shaped")
    parser.add_argument("--base-checkpoint", default=None)
    parser.add_argument("--output-dir", default="./grpo_v1")
    parser.add_argument("--no-vllm", action="store_true")
    main(parser.parse_args())
