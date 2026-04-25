"""
F1 Strategist — Track Loader
==============================

Reads racetrack-database CSVs from data/tracks/ into a Track object that
exposes centerline, length, corners, pit-loss, DRS zones, and a track-character
label.

Owner: Person 1.
Spec: docs/architecture.md §3, docs/physics-model.md §calibration-data.

TODO:
    - Phase 1: load_track(name) → Track from CSV
    - Phase 1: detect_corners(curvature_array) → list[Corner]
    - Phase 1: TRACK_CHARACTER table for the 5 chosen tracks
    - Phase 2: PIT_LOSS table per track (green-flag and SC values)
    - Phase 2: DRS_ZONES per track (start/end distances along centerline)

Track-character options: "power" | "balanced" | "downforce" | "street" | "weather_prone"
"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Corner:
    name: str
    distance_m: float
    radius_m: float
    direction: str  # "L" | "R"


@dataclass
class Track:
    name: str
    centerline: np.ndarray  # shape (N, 2) in metres
    length_m: float
    corners: list[Corner]
    pit_lane_loss_s: float
    sc_pit_loss_s: float
    drs_zones: list[tuple[float, float]]
    track_character: str


def load_track(name: str) -> Track:
    """Load a track from data/tracks/<name>.csv. Raises if missing."""
    raise NotImplementedError("Phase 1, Person 1")


def detect_corners(curvature: np.ndarray, distance: np.ndarray) -> list[Corner]:
    """Cluster contiguous high-|κ| segments into corners."""
    raise NotImplementedError("Phase 1, Person 1")
