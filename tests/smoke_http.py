"""
HTTP smoke test against the OpenEnv server.

Boots a local server (or hits a passed --base-url) and confirms:
    1. /health returns 200 with {"status": "ok"}
    2. /reset returns 200 with valid F1Observation (total_issues_count > 0)
    3. /step with STAY_OUT returns 200, done == False
    4. /step with garbage returns reward == -0.02
    5. /step with DONE flips done == True

CLI:
    # Local
    python tests/smoke_http.py
    # Remote
    python tests/smoke_http.py --base-url https://Deltasthic-f1-strategist.hf.space
"""
import argparse
import json
import sys
import time
from urllib.request import urlopen, Request


def post_json(url: str, payload: dict) -> dict:
    req = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def get_json(url: str) -> dict:
    with urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())


def run(base_url: str) -> int:
    failures = 0

    # 1. /health
    try:
        h = get_json(f"{base_url}/health")
        assert h.get("status") in {"ok", "healthy"}, f"health: {h}"
        print("  ok: /health")
    except Exception as e:
        print(f"FAIL: /health -> {e}")
        failures += 1

    # 2. /reset
    try:
        obs = post_json(f"{base_url}/reset", {})
        total = obs.get("observation", {}).get("total_issues_count", 0)
        assert total > 0, f"reset returned total_issues_count={total}"
        print(f"  ok: /reset (total_issues_count={total})")
    except Exception as e:
        print(f"FAIL: /reset -> {e}")
        failures += 1

    # 3. /step STAY_OUT
    try:
        r = post_json(f"{base_url}/step", {"action": {"command": "STAY_OUT"}})
        assert r.get("done") is False, f"step STAY_OUT: done={r.get('done')}"
        print("  ok: /step STAY_OUT")
    except Exception as e:
        print(f"FAIL: /step STAY_OUT -> {e}")
        failures += 1

    # 4. /step garbage → -0.02
    try:
        r = post_json(f"{base_url}/step", {"action": {"command": "ZZZZ_NOT_A_COMMAND"}})
        assert abs(r.get("reward", 0.0) - (-0.02)) < 1e-6, f"step garbage: reward={r.get('reward')}"
        print("  ok: /step garbage (-0.02)")
    except Exception as e:
        print(f"FAIL: /step garbage -> {e}")
        failures += 1

    # 5. /step DONE
    try:
        r = post_json(f"{base_url}/step", {"action": {"command": "DONE"}})
        assert r.get("done") is True, f"step DONE: done={r.get('done')}"
        print("  ok: /step DONE")
    except Exception as e:
        print(f"FAIL: /step DONE -> {e}")
        failures += 1

    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()
    print(f"Smoke testing {args.base_url}")
    failures = run(args.base_url)
    if failures:
        print(f"\n{failures} check(s) failed.")
        sys.exit(1)
    print("\nAll 5 checks passed.")


if __name__ == "__main__":
    main()
