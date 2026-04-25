# data/

Track geometry and calibration constants. **All files here are committed to git** so
both the local env and the HF Space have everything they need at boot — no runtime
downloads.

## Contents

```
data/
├── README.md                            (this file)
├── tracks/                              (one CSV per track — see tracks/README.md)
│   ├── README.md
│   ├── Monza.csv
│   ├── Monaco.csv
│   ├── Catalunya.csv
│   ├── Spa.csv
│   └── Silverstone.csv
├── opponent_pace_calibration.json       (per-track lap-time stats from Kaggle)
└── tyre_compound_baseline.json          (compound pace deltas + wear rates)
```

## Generation

The two JSON files are not hand-edited. Regenerate with:

```bash
# Lap-time / pit-loss / opponent-pace distributions from archive.zip (Kaggle)
python scripts/calibrate_opponent_pace.py

# Tyre baselines (defaults from docs/physics-model.md, can be tuned)
python scripts/calibrate_tyre_baseline.py
```

Track CSVs are extracted from `racetrack-database-master.zip`:

```bash
python scripts/extract_track_csvs.py --source /path/to/racetrack-database-master
```

## Provenance

- **Kaggle Formula 1 World Championship dataset (1950–2024)** — `archive.zip`
  source for `opponent_pace_calibration.json`. Public, commercial-use OK.
- **TUMFTM racetrack-database** (MIT licensed) — `racetrack-database-master.zip`
  source for `tracks/*.csv`. The dataset does NOT include Monaco or Spa; we
  substitute geometric proxies and override timings from Kaggle. See
  `tracks/README.md` for substitution map.
- **OpenF1 API documentation** — only used to confirm vocabulary (DRS encoding,
  compound names, weather field semantics). NOT called at runtime.
- **FastF1 library** — included for reference reading only. NOT a runtime dep.

## Schema

### `opponent_pace_calibration.json`

```json
{
  "<track_name>": {
    "base_lap_time_s": float,    // median lap time, modern era (2014–2024)
    "lap_time_p25":    float,    // 25th percentile
    "lap_time_p75":    float,    // 75th percentile
    "median_pit_loss_s": float,  // median pit-stop time loss
    "n_samples":       int       // count of laps in the calibration set
  }
}
```

### `tyre_compound_baseline.json`

```json
{
  "<compound>": {
    "pace_delta_s":             float,  // s/lap vs medium reference, fresh tyres, dry
    "wear_rate":                float,  // health fraction lost per lap, race mode, 30°C
    "wear_penalty_s_per_unit":  float   // s/lap added per unit of health lost
  }
}
```

Compounds: `soft`, `medium`, `hard`, `inter`, `wet`.
