"""
Calibrate per-track lap-time distributions from archive.zip (Kaggle F1 dataset).

Owner: Person 2.

Reads:
    archive/lap_times.csv  — every recorded lap (~17 MB)
    archive/circuits.csv   — circuit metadata
    archive/races.csv      — to filter by year (2014-2024 only — modern era)

Outputs:
    data/opponent_pace_calibration.json:
        {
            "Monza": {
                "base_lap_time_s": 81.5,
                "lap_time_p25": 80.8,
                "lap_time_p75": 82.6,
                "median_pit_loss_s": 22.0,
                "n_samples": 4392
            },
            "Monaco": ...
        }

Used by:
    server/opponents.py — sample opponent pace_offset_s
    server/physics.py   — base_lap_time per track

CLI:
    python scripts/calibrate_opponent_pace.py
    python scripts/calibrate_opponent_pace.py --source /path/to/archive
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="archive")
    parser.add_argument("--output", default="data/opponent_pace_calibration.json")
    parser.add_argument("--year-min", type=int, default=2014)
    parser.add_argument("--year-max", type=int, default=2024)
    args = parser.parse_args()
    # TODO Phase 0 (Person 2):
    #   1. pd.read_csv(archive/circuits.csv) → circuitId → name
    #   2. pd.read_csv(archive/races.csv) → filter by year, get raceIds
    #   3. pd.read_csv(archive/lap_times.csv) → join on raceId → group by circuit → median, p25, p75
    #   4. pd.read_csv(archive/pit_stops.csv) → median per circuit
    #   5. dump dict → JSON
    print("calibrate_opponent_pace.py — TODO Phase 0, Person 2")


if __name__ == "__main__":
    main()
