"""
F1 Strategist — Postmortem Memory
===================================

Append-only .jsonl episode-failure memory. After each episode, classifies the
failure mode, records it, and on the next reset retrieves the top-2 lowest-
scoring past records for the same scenario family as memory hints.

Owner: Person 1.
Spec: docs/architecture.md §postmortem (in the loop), docs/build-order.md §Phase-4.

Storage: baselines/trajectories/postmortems.jsonl

Failure categories:
    missed_undercut   — ASSESS_UNDERCUT_WINDOW never called
    late_weather_call — rain peak passed without inter pit
    fuel_underburn    — finished above target fuel margin (drag penalty)
    cascade_ignored   — blast-radius edge revealed but not addressed
    comms_forgotten   — pending_comms unresolved at episode end
    panic_pit         — 2 pits within 3 laps without SC/weather justification
    thrashing         — same action 3+ times consecutively

TODO Phase 4:
    - record(summary)
    - retrieve(family, k=2)
    - classify_failure(audit_trail, final_scores)
    - inject into reset()'s observation.memory_hints
"""
from datetime import datetime
import json
from pathlib import Path


class PostmortemMemory:
    PATH = Path("baselines/trajectories/postmortems.jsonl")

    @classmethod
    def record(cls, summary: dict) -> None:
        raise NotImplementedError("Phase 4, Person 1")

    @classmethod
    def retrieve(cls, scenario_family: str, k: int = 2) -> list[dict]:
        raise NotImplementedError("Phase 4, Person 1")

    @classmethod
    def classify_failure(cls, audit_trail: list, final_scores: dict) -> str:
        raise NotImplementedError("Phase 4, Person 1")
