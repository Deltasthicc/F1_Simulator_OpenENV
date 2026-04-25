"""
Copy the chosen tracks from racetrack-database-master/ into data/tracks/
with normalised column names.

Owner: Person 1.

The TUMFTM racetrack-database CSV columns are:
    x_m, y_m, w_tr_right_m, w_tr_left_m, x_normvec_m, y_normvec_m,
    alpha_m, s_racetraj_m, psi_racetraj_rad, kappa_racetraj_radpm,
    vx_racetraj_mps, ax_racetraj_mps2

We keep all columns. The visualizer uses (x_m, y_m); track.py uses
kappa_racetraj_radpm + s_racetraj_m for corner detection.

Tracks chosen:
    Monza        — power circuit (use Hockenheim as a substitute geometry — F1 doesn't
                   include Monza in the open dataset, but we override timings from Kaggle)
    Catalunya    — balanced
    Melbourne    — alternate balanced (kept for procedural generator coverage)
    BrandsHatch  — Monaco substitute (street character, override timings)
    Budapest     — downforce circuit (alternate)
    Austin       — power-balanced (alternate)

If your team prefers a different lineup, edit TRACKS_TO_COPY below.

CLI:
    python scripts/extract_track_csvs.py
    python scripts/extract_track_csvs.py --source /path/to/racetrack-database-master
"""
import argparse
import shutil
from pathlib import Path

TRACKS_TO_COPY = [
    "Hockenheim",   # → renamed to Monza for our purposes (timing override applied)
    "Catalunya",
    "Melbourne",
    "BrandsHatch",  # → renamed to Monaco for our purposes
    "Budapest",
    "Austin",
]

# The names we use internally → source CSV name
ALIAS_MAP = {
    "Monza":       "Hockenheim",
    "Catalunya":   "Catalunya",
    "Melbourne":   "Melbourne",
    "Monaco":      "BrandsHatch",
    "Spa":         "Budapest",      # rough geometric proxy; timings override from Kaggle
    "Silverstone": "Austin",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="racetrack-database-master/racelines")
    parser.add_argument("--dest", default="data/tracks")
    args = parser.parse_args()

    src = Path(args.source)
    dst = Path(args.dest)
    dst.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        print(f"Source {src} not found. Unzip racetrack-database-master.zip first.")
        return

    for our_name, source_name in ALIAS_MAP.items():
        src_csv = src / f"{source_name}.csv"
        dst_csv = dst / f"{our_name}.csv"
        if not src_csv.exists():
            print(f"  skip: {src_csv} not found")
            continue
        shutil.copy(src_csv, dst_csv)
        print(f"  ok: {our_name}.csv ← {source_name}.csv")

    print("Done. Spot-check lengths in track.py before continuing.")


if __name__ == "__main__":
    main()
