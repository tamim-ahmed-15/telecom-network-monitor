"""Generate the Version 1 normal synthetic telecom monitoring dataset.

This generator intentionally creates NORMAL network behavior only.
Anomaly injection will be added after the normal data has been validated.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from simulator.config import (
    CELL_PROFILES,
    DAYS,
    INTERVAL_MINUTES,
    LOCATION_TYPES,
    RAW_OUTPUT_PATH,
    REGIONS,
    SAMPLE_OUTPUT_PATH,
    SAMPLE_ROWS,
    SEED,
    START_DATE,
    TECHNOLOGY,
    UPLOAD_RATIO_RANGE,
)


OUTPUT_COLUMNS = [
    "timestamp",
    "cell_id",
    "region",
    "location_type",
    "technology",
    "connected_users",
    "download_traffic_gb",
    "upload_traffic_gb",
    "throughput_mbps",
    "latency_ms",
    "packet_loss_percent",
    "signal_quality_dbm",
    "cpu_usage_percent",
    "memory_usage_percent",
    "handover_count",
    "is_anomaly",
    "anomaly_type",
    "anomaly_id",
]


def _gaussian_peak(hour: float, center: float, width: float) -> float:
    """Return a smooth daily peak, accounting for the 24-hour wraparound."""
    distance = min(abs(hour - center), 24 - abs(hour - center))
    return math.exp(-0.5 * (distance / width) ** 2)


def activity_level(location_type: str, hour: float, is_weekend: bool) -> float:
    """Return a normalized 0-1 activity level for a cell type."""

    if location_type == "Residential":
        level = (
            0.12
            + 0.18 * _gaussian_peak(hour, 8.0, 2.2)
            + 0.78 * _gaussian_peak(hour, 20.0, 3.1)
        )
        if is_weekend:
            level *= 1.08

    elif location_type == "Business":
        level = 0.07 + 0.88 * _gaussian_peak(hour, 13.0, 3.6)
        if is_weekend:
            level *= 0.55

    elif location_type == "University":
        level = 0.08 + 0.84 * _gaussian_peak(hour, 13.0, 3.5)
        if is_weekend:
            level *= 0.65

    elif location_type == "Transport":
        level = (
            0.12
            + 0.65 * _gaussian_peak(hour, 8.5, 1.8)
            + 0.72 * _gaussian_peak(hour, 18.0, 2.0)
        )
        if is_weekend:
            level *= 0.85

    elif location_type == "Suburban":
        level = (
            0.12
            + 0.22 * _gaussian_peak(hour, 12.0, 4.2)
            + 0.58 * _gaussian_peak(hour, 20.0, 3.4)
        )
        if is_weekend:
            level *= 1.04

    else:
        raise ValueError(f"Unknown location type: {location_type}")

    return float(np.clip(level, 0.05, 1.0))


def build_cells(rng: np.random.Generator) -> list[dict]:
    """Create the 20 synthetic cells with small cell-to-cell differences."""
    cells = []

    for region, prefix in REGIONS.items():
        for index, location_type in enumerate(LOCATION_TYPES, start=1):
            base = CELL_PROFILES[location_type]

            cells.append(
                {
                    "cell_id": f"{prefix}_{index:03d}",
                    "region": region,
                    "location_type": location_type,
                    "technology": TECHNOLOGY,
                    "user_capacity": int(
                        round(base["user_capacity"] * rng.uniform(0.92, 1.08))
                    ),
                    "capacity_mbps": (
                        base["capacity_mbps"] * rng.uniform(0.94, 1.06)
                    ),
                    "baseline_latency_ms": (
                        base["baseline_latency_ms"] + rng.uniform(-2.0, 2.0)
                    ),
                    "baseline_signal_dbm": (
                        base["baseline_signal_dbm"] + rng.uniform(-2.0, 2.0)
                    ),
                    "base_cpu_percent": (
                        base["base_cpu_percent"] + rng.uniform(-2.0, 2.0)
                    ),
                    "base_memory_percent": (
                        base["base_memory_percent"] + rng.uniform(-2.0, 2.0)
                    ),
                    "per_user_mbps": (
                        base["per_user_mbps"] * rng.uniform(0.92, 1.08)
                    ),
                    "handover_base": (
                        base["handover_base"] * rng.uniform(0.90, 1.10)
                    ),
                }
            )

    return cells


def _normal_packet_loss(
    rng: np.random.Generator,
    load_ratio: float,
    signal_penalty: float,
) -> float:
    """Generate zero-heavy, right-skewed NORMAL packet loss."""

    draw = rng.random()

    if draw < 0.55:
        packet_loss = 0.0
    elif draw < 0.90:
        packet_loss = rng.gamma(shape=1.1, scale=0.16)
    else:
        packet_loss = rng.gamma(shape=1.2, scale=0.38)

    # Mild load/signal effects only. Large degradation is reserved for anomalies.
    packet_loss += 2.5 * max(0.0, load_ratio - 0.78) ** 2
    packet_loss += 0.18 * signal_penalty

    return float(np.clip(packet_loss, 0.0, 1.8))


def generate_normal_dataset() -> pd.DataFrame:
    """Generate 20 cells x 14 days x 15-minute normal KPI observations."""
    rng = np.random.default_rng(SEED)
    cells = build_cells(rng)

    periods = DAYS * 24 * (60 // INTERVAL_MINUTES)

    timestamps = pd.date_range(
        start=START_DATE,
        periods=periods,
        freq=f"{INTERVAL_MINUTES}min",
    )

    rows = []

    for cell in cells:
        # Memory is stateful so it changes more slowly than CPU.
        memory_state = cell["base_memory_percent"]

        for timestamp in timestamps:
            hour = timestamp.hour + timestamp.minute / 60.0
            is_weekend = timestamp.dayofweek >= 5

            activity = activity_level(
                cell["location_type"],
                hour,
                is_weekend,
            )

            # Users follow cell personality + time of day + small natural noise.
            occupancy = np.clip(
                0.06 + 0.82 * activity + rng.normal(0.0, 0.025),
                0.03,
                0.94,
            )

            connected_users = max(
                1,
                int(round(cell["user_capacity"] * occupancy)),
            )

            # Average offered data rate generated by each connected user.
            per_user_mbps = (
                cell["per_user_mbps"]
                * (0.78 + 0.42 * activity)
                * rng.normal(1.0, 0.055)
            )

            offered_load_mbps = max(
                0.2,
                connected_users * per_user_mbps,
            )

            load_ratio = offered_load_mbps / cell["capacity_mbps"]

            # Synthetic RSRP-like signal value.
            weekly_drift = math.sin(
                2 * math.pi * (timestamp.dayofyear % 7) / 7
            )

            signal_quality_dbm = (
                cell["baseline_signal_dbm"]
                + rng.normal(0.0, 2.1)
                + weekly_drift
            )

            signal_quality_dbm = float(
                np.clip(signal_quality_dbm, -103.0, -68.0)
            )

            # Only weak signal values receive a mild performance penalty.
            signal_penalty = max(
                0.0,
                (-92.0 - signal_quality_dbm) / 18.0,
            )

            # RANalyzer showed that normal throughput usually tracks offered load
            # efficiently, so normal efficiency remains close to 1.
            efficiency_center = (
                0.992
                - 0.05 * max(0.0, load_ratio - 0.82)
                - 0.018 * signal_penalty
            )

            efficiency = float(
                np.clip(
                    rng.normal(efficiency_center, 0.007),
                    0.90,
                    1.01,
                )
            )

            throughput_mbps = (
                min(offered_load_mbps, cell["capacity_mbps"])
                * efficiency
            )

            packet_loss_percent = _normal_packet_loss(
                rng,
                load_ratio,
                signal_penalty,
            )

            latency_ms = (
                cell["baseline_latency_ms"]
                + rng.normal(0.0, 1.4)
                + 14.0 * max(0.0, load_ratio - 0.75) ** 2
                + 2.5 * signal_penalty
            )

            latency_ms = float(
                np.clip(latency_ms, 18.0, 65.0)
            )

            cpu_usage_percent = (
                cell["base_cpu_percent"]
                + 48.0 * min(load_ratio, 1.2)
                + rng.normal(0.0, 2.3)
            )

            cpu_usage_percent = float(
                np.clip(cpu_usage_percent, 12.0, 86.0)
            )

            # Slow-moving memory state.
            memory_target = (
                cell["base_memory_percent"]
                + 15.0 * min(load_ratio, 1.1)
            )

            memory_state = (
                0.93 * memory_state
                + 0.07 * memory_target
                + rng.normal(0.0, 0.35)
            )

            memory_usage_percent = float(
                np.clip(memory_state, 25.0, 84.0)
            )

            # Convert achieved downlink throughput to GB transferred in 15 min.
            interval_seconds = INTERVAL_MINUTES * 60

            download_traffic_gb = (
                throughput_mbps
                * interval_seconds
                / (8 * 1000)
            )

            download_traffic_gb *= rng.normal(1.0, 0.025)
            download_traffic_gb = max(0.0, download_traffic_gb)

            upload_ratio = rng.uniform(*UPLOAD_RATIO_RANGE)

            upload_traffic_gb = (
                download_traffic_gb
                * upload_ratio
                * rng.normal(1.0, 0.04)
            )

            upload_traffic_gb = max(0.0, upload_traffic_gb)

            handover_mean = (
                cell["handover_base"]
                * (0.55 + 0.90 * activity)
            )

            handover_count = int(
                rng.poisson(max(handover_mean, 0.5))
            )

            rows.append(
                {
                    "timestamp": timestamp,
                    "cell_id": cell["cell_id"],
                    "region": cell["region"],
                    "location_type": cell["location_type"],
                    "technology": cell["technology"],
                    "connected_users": connected_users,
                    "download_traffic_gb": round(download_traffic_gb, 4),
                    "upload_traffic_gb": round(upload_traffic_gb, 4),
                    "throughput_mbps": round(throughput_mbps, 3),
                    "latency_ms": round(latency_ms, 3),
                    "packet_loss_percent": round(packet_loss_percent, 4),
                    "signal_quality_dbm": round(signal_quality_dbm, 3),
                    "cpu_usage_percent": round(cpu_usage_percent, 3),
                    "memory_usage_percent": round(memory_usage_percent, 3),
                    "handover_count": handover_count,
                    "is_anomaly": 0,
                    "anomaly_type": "normal",
                    "anomaly_id": None,
                }
            )

    df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)

    return df.sort_values(
        ["cell_id", "timestamp"]
    ).reset_index(drop=True)


def save_dataset(df: pd.DataFrame) -> None:
    """Save the full ignored dataset and a small GitHub-safe sample."""
    raw_path = Path(RAW_OUTPUT_PATH)
    sample_path = Path(SAMPLE_OUTPUT_PATH)

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    sample_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(raw_path, index=False)

    df.head(SAMPLE_ROWS).to_csv(
        sample_path,
        index=False,
    )

    print(f"Full dataset saved to: {raw_path}")
    print(f"Sample dataset saved to: {sample_path}")


def main() -> None:
    df = generate_normal_dataset()
    save_dataset(df)

    print()
    print("Normal telecom dataset generated successfully.")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Cells: {df['cell_id'].nunique()}")
    print(f"Anomalous rows: {df['is_anomaly'].sum()}")


if __name__ == "__main__":
    main()
