"""
Push a trained checkpoint to the HuggingFace Hub.

Owner: Person 2.

CLI:
    python scripts/push_checkpoint.py
    python scripts/push_checkpoint.py --checkpoint ./grpo_v1/checkpoint-best --repo Deltasthic/f1-strategist-qwen3-4b-grpo
"""
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="./grpo_v1/checkpoint-best")
    parser.add_argument("--repo", default="Deltasthic/f1-strategist-qwen3-4b-grpo")
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args()
    # TODO Phase 3:
    #   from huggingface_hub import HfApi
    #   api = HfApi()
    #   api.create_repo(args.repo, repo_type="model", private=args.private, exist_ok=True)
    #   api.upload_folder(folder_path=args.checkpoint, repo_id=args.repo)
    print(f"push_checkpoint.py — TODO Phase 3 — push {args.checkpoint} → {args.repo}")


if __name__ == "__main__":
    main()
