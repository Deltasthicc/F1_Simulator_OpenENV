<<<<<<< HEAD
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
=======
# data/tracks/

One CSV per track, copied verbatim from the [TUMFTM racetrack-database](https://github.com/TUMFTM/racetrack-database).

## CSV format

Each file has a single comment header and four data columns:

```
# x_m,y_m,w_tr_right_m,w_tr_left_m
-0.320123,1.087714,5.739,5.932
0.168262,6.062191,5.735,5.929
...
```

- `x_m`, `y_m` — centerline position in metres
- `w_tr_right_m`, `w_tr_left_m` — track width either side of the centerline

The track is a closed loop; the last row is approximately equal to the first.
`server/track.py` handles the closure, computes total length from pairwise
distances, derives curvature via central differences, and detects corners by
thresholding the smoothed curvature signal.

## License

The track data is **LGPL-3.0** (TUMFTM). Distribution alongside our MIT-licensed
project code is permitted; redistribution must preserve the LGPL notice. See
`racetrack-database-master/LICENSE` after extraction.

## The 25 included tracks

| # | Track | Country | F1? | Character | Length (m) | Source |
|---|---|---|---|---|---|---|
| 1 | Austin | USA | yes | balanced | ~5510 | F1 |
| 2 | BrandsHatch | UK | no (DTM) | street | ~3920 | DTM |
| 3 | Budapest | Hungary | yes | downforce | ~4380 | F1 (Hungaroring) |
| 4 | Catalunya | Spain | yes | balanced | ~4660 | F1 |
| 5 | Hockenheim | Germany | retired | balanced | ~4570 | F1 1970–2018 |
| 6 | IMS | USA | no (IndyCar) | power | ~4190 | IndyCar road course |
| 7 | Melbourne | Australia | yes | balanced | ~5280 | F1 |
| 8 | MexicoCity | Mexico | yes | power | ~4300 | F1 |
| 9 | Montreal | Canada | yes | power | ~4360 | F1 |
| 10 | Monza | Italy | yes | power | ~5790 | F1 |
| 11 | MoscowRaceway | Russia | no (DTM) | balanced | ~4070 | DTM |
| 12 | Norisring | Germany | no (DTM) | street | ~2300 | DTM |
| 13 | Nuerburgring | Germany | retired | balanced | ~5150 | F1 GP layout |
| 14 | Oschersleben | Germany | no (DTM) | balanced | ~3700 | DTM |
| 15 | Sakhir | Bahrain | yes | power | ~5410 | F1 |
| 16 | SaoPaulo | Brazil | yes | power | ~4310 | F1 (Interlagos) |
| 17 | Sepang | Malaysia | retired | balanced | ~5540 | F1 1999–2017 |
| 18 | Shanghai | China | yes | balanced | ~5450 | F1 |
| 19 | Silverstone | UK | yes | balanced | ~5890 | F1 |
| 20 | Sochi | Russia | retired | balanced | ~5850 | F1 2014–2021 |
| 21 | Spa | Belgium | yes | weather_prone | ~7000 | F1 |
| 22 | Spielberg | Austria | yes | power | ~4320 | F1 (Red Bull Ring) |
| 23 | Suzuka | Japan | yes | balanced | ~5810 | F1 |
| 24 | YasMarina | UAE | yes | downforce | ~5280 | F1 (post-2021 layout) |
| 25 | Zandvoort | Netherlands | yes | downforce | ~4260 | F1 (returned 2021) |

(Lengths are approximate centerline values — `track.py` computes the exact value at load time.)

**18 are real F1 venues** (current, retired, or returning). The remaining 7 are
DTM/IndyCar circuits we keep for the procedural generator's coverage. Track
character labels feed `server/physics.py` — they're hand-curated, not data-derived.

## Monaco substitution

The TUMFTM dataset does **not** include Monaco. Two options for Family-3 (Late
Safety Car) scenarios:

1. **Use BrandsHatch** as the street-character substitute. Same `character: "street"`,
   similar pit-lane loss, similar low-overtaking dynamics. The hand-authored
   scenario `late_safety_car_monaco` stays narratively-named "Monaco" but loads
   `data/tracks/BrandsHatch.csv`. This is the recommended path.
2. Generate a synthetic Monaco centerline (cubic-spline approximation from a
   handful of waypoints). Phase 5 work, optional.

We go with option 1 by default. The visualiser will render the BrandsHatch
shape; the strategic decisions and scoring are unaffected.

## Validation

After `scripts/extract_track_csvs.py` runs, spot-check:

```bash
python -c "
from server.track import load_track
for name in ['Monza', 'Spa', 'Catalunya', 'Suzuka', 'Silverstone', 'Spielberg']:
    t = load_track(name)
    print(f'{name}: {t.length_m:.0f} m, {len(t.corners)} corners, {t.track_character}')
"
```

Expected lengths (approximate, derived from centerline):
- Monza ≈ 5790 m
- Spa ≈ 7000 m
- Catalunya ≈ 4660 m
- Suzuka ≈ 5810 m
- Silverstone ≈ 5890 m
- Spielberg ≈ 4320 m

If a length is off by more than 5%, something went wrong in the copy or the
length computation. Inspect the CSV's first/last rows to check for a missing
closure point.

## Curated metadata

Per-track defaults (character, base lap time, pit-loss green/SC, DRS zones)
live in `../track_metadata.json`. That file is hand-curated and committed to
git. Person 2's `scripts/calibrate_opponent_pace.py` may overwrite the
`base_lap_time_s` value with Kaggle-derived medians but does NOT touch the
character labels.
>>>>>>> 4323b3e (Added env and scoring and basic READMEs)
