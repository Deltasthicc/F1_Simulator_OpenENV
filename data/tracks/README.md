# data/tracks/

One CSV per track, normalised from the TUMFTM racetrack-database CSVs.

## Columns

```
x_m, y_m, w_tr_right_m, w_tr_left_m,
x_normvec_m, y_normvec_m, alpha_m,
s_racetraj_m, psi_racetraj_rad, kappa_racetraj_radpm,
vx_racetraj_mps, ax_racetraj_mps2
```

Used by:
- `server/track.py` — `(s_racetraj_m, kappa_racetraj_radpm)` for corner detection
- `server/visualizer.py` — `(x_m, y_m)` for the top-down render

Units: metres for distances, m/s for velocity, m/s² for accel, rad and rad/m for angles.

## Substitution map

The TUMFTM dataset does not include Monaco or Spa. We use geometric proxies and
override timings from the Kaggle calibration. The naming we use internally is
the F1 track name; the underlying CSV may come from a different source.

| Internal name | Source CSV from racetrack-database | Reason |
|---|---|---|
| Monza        | Hockenheim     | Power-circuit proxy. Timings overridden from Kaggle. |
| Catalunya    | Catalunya      | Native. |
| Melbourne    | Melbourne      | Native. (Procedural-generator alternate) |
| Monaco       | BrandsHatch    | Street-character proxy. Timings overridden. |
| Spa          | Budapest       | Geometric proxy with weather-prone label. Timings overridden. |
| Silverstone  | Austin         | Power-balanced proxy. Timings overridden. |

If you find better substitutes (e.g. by manually constructing a Monaco
centerline), update both this table and `scripts/extract_track_csvs.py`.

## Validation

After running `extract_track_csvs.py`, spot-check each file loads cleanly:

```python
import pandas as pd
for t in ["Monza", "Monaco", "Catalunya", "Spa", "Silverstone"]:
    df = pd.read_csv(f"data/tracks/{t}.csv")
    print(f"{t}: {len(df)} rows, length {df['s_racetraj_m'].max():.1f} m")
```

Expected lengths (track-character proxy, NOT real F1 lengths):
- Hockenheim ≈ 4574 m
- Catalunya ≈ 4655 m (real Catalunya ≈ 4657 m, very close)
- BrandsHatch ≈ 3908 m
- Budapest ≈ 4381 m
- Austin ≈ 5513 m
