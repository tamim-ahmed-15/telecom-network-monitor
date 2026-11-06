"""Inject controlled anomaly events into the normal telecom dataset.

The original normal dataset is never modified in place.

Run:
    python -m simulator.anomaly_injector
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from simulator.anomaly_config import (
    ANOMALY_OUTPUT_PATH,
    ANOMALY_SAMPLE_PATH,
    ANOMALY_SEED,
    ANOMALY_SPECS,
    EVENT_GUARD_INTERVALS,
    EVENT_MANIFEST_PATH,
    TARGET_ANOMALY_FRACTION,
)
from simulator.config import INTERVAL_MINUTES, RAW_OUTPUT_PATH


def _recompute_download_traffic(
    df: pd.DataFrame,
    indices: np.ndarray,
    rng: np.random.Generator,
) -> None:
    """Keep delivered downlink volume consistent with achieved throughput."""
    interval_seconds = INTERVAL_MINUTES * 60

    traffic = (
        df.loc[indices, "throughput_mbps"].to_numpy()
        * interval_seconds
        / (8 * 1000)
    )

    traffic *= rng.uniform(0.98, 1.02, size=len(indices))

    df.loc[indices, "download_traffic_gb"] = np.maximum(
        traffic,
        0.0,
    ).round(4)


def _apply_anomaly(
    df: pd.DataFrame,
    indices: np.ndarray,
    anomaly_type: str,
    rng: np.random.Generator,
) -> None:
    """Modify KPI values for one contiguous anomaly event."""

    n = len(indices)

    if anomaly_type == "latency_spike":
        factor = rng.uniform(3.0, 5.5)
        row_factor = factor * rng.uniform(0.94, 1.06, size=n)

        df.loc[indices, "latency_ms"] = np.clip(
            df.loc[indices, "latency_ms"].to_numpy() * row_factor,
            70.0,
            300.0,
        ).round(3)

    elif anomaly_type == "packet_loss_spike":
        event_level = rng.uniform(5.0, 18.0)
        values = event_level * rng.uniform(0.88, 1.12, size=n)

        df.loc[indices, "packet_loss_percent"] = np.clip(
            np.maximum(
                df.loc[indices, "packet_loss_percent"].to_numpy(),
                values,
            ),
            0.0,
            30.0,
        ).round(4)

    elif anomaly_type == "throughput_degradation":
        factor = rng.uniform(0.30, 0.60)
        row_factor = factor * rng.uniform(0.94, 1.06, size=n)

        df.loc[indices, "throughput_mbps"] = np.maximum(
            df.loc[indices, "throughput_mbps"].to_numpy() * row_factor,
            0.1,
        ).round(3)

        _recompute_download_traffic(df, indices, rng)

    elif anomaly_type == "traffic_surge":
        user_factor = rng.uniform(1.30, 1.70)
        traffic_factor = rng.uniform(1.25, 1.55)

        users = (
            df.loc[indices, "connected_users"].to_numpy()
            * user_factor
            * rng.uniform(0.96, 1.04, size=n)
        )

        df.loc[indices, "connected_users"] = np.clip(
            np.rint(users),
            1,
            850,
        ).astype(int)

        df.loc[indices, "throughput_mbps"] = np.clip(
            df.loc[indices, "throughput_mbps"].to_numpy()
            * traffic_factor
            * rng.uniform(0.96, 1.04, size=n),
            0.1,
            125.0,
        ).round(3)

        _recompute_download_traffic(df, indices, rng)

        df.loc[indices, "upload_traffic_gb"] = np.maximum(
            df.loc[indices, "upload_traffic_gb"].to_numpy()
            * rng.uniform(1.35, 1.90)
            * rng.uniform(0.96, 1.04, size=n),
            0.0,
        ).round(4)

        df.loc[indices, "cpu_usage_percent"] = np.clip(
            df.loc[indices, "cpu_usage_percent"].to_numpy()
            + rng.uniform(10.0, 20.0)
            + rng.normal(0.0, 1.0, size=n),
            0.0,
            95.0,
        ).round(3)

        df.loc[indices, "latency_ms"] = np.clip(
            df.loc[indices, "latency_ms"].to_numpy()
            * rng.uniform(1.05, 1.18),
            0.1,
            80.0,
        ).round(3)

        df.loc[indices, "packet_loss_percent"] = np.clip(
            df.loc[indices, "packet_loss_percent"].to_numpy()
            + rng.uniform(0.05, 0.65, size=n),
            0.0,
            2.5,
        ).round(4)

    elif anomaly_type == "cpu_overload":
        overload = rng.uniform(90.0, 98.5)
        values = overload + rng.normal(0.0, 1.0, size=n)

        df.loc[indices, "cpu_usage_percent"] = np.clip(
            np.maximum(
                df.loc[indices, "cpu_usage_percent"].to_numpy(),
                values,
            ),
            90.0,
            99.0,
        ).round(3)

    elif anomaly_type == "memory_overload":
        overload = rng.uniform(90.0, 98.0)
        values = overload + rng.normal(0.0, 0.8, size=n)

        df.loc[indices, "memory_usage_percent"] = np.clip(
            np.maximum(
                df.loc[indices, "memory_usage_percent"].to_numpy(),
                values,
            ),
            90.0,
            99.0,
        ).round(3)

        df.loc[indices, "cpu_usage_percent"] = np.clip(
            df.loc[indices, "cpu_usage_percent"].to_numpy()
            + rng.uniform(0.0, 5.0, size=n),
            0.0,
            95.0,
        ).round(3)

    elif anomaly_type == "multi_kpi_degradation":
        latency_factor = rng.uniform(2.0, 4.0)
        throughput_factor = rng.uniform(0.30, 0.60)
        loss_level = rng.uniform(5.0, 15.0)

        df.loc[indices, "latency_ms"] = np.clip(
            df.loc[indices, "latency_ms"].to_numpy()
            * latency_factor
            * rng.uniform(0.95, 1.05, size=n),
            60.0,
            250.0,
        ).round(3)

        df.loc[indices, "packet_loss_percent"] = np.clip(
            loss_level * rng.uniform(0.90, 1.10, size=n),
            4.0,
            20.0,
        ).round(4)

        df.loc[indices, "throughput_mbps"] = np.maximum(
            df.loc[indices, "throughput_mbps"].to_numpy()
            * throughput_factor
            * rng.uniform(0.95, 1.05, size=n),
            0.1,
        ).round(3)

        _recompute_download_traffic(df, indices, rng)

        df.loc[indices, "cpu_usage_percent"] = np.clip(
            df.loc[indices, "cpu_usage_percent"].to_numpy()
            + rng.uniform(15.0, 30.0)
            + rng.normal(0.0, 1.0, size=n),
            0.0,
            99.0,
        ).round(3)

    else:
        raise ValueError(f"Unknown anomaly type: {anomaly_type}")


def inject_anomalies(
    normal_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return a labeled anomaly dataset and an event manifest."""

    rng = np.random.default_rng(ANOMALY_SEED)

    df = normal_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["cell_id", "timestamp"]).reset_index(drop=True)

    df["is_anomaly"] = 0
    df["anomaly_type"] = "normal"
    df["anomaly_id"] = pd.Series([None] * len(df), dtype="object")

    target_rows = int(round(len(df) * TARGET_ANOMALY_FRACTION))
    anomaly_types = list(ANOMALY_SPECS)

    cell_indices = {
        cell_id: group.index.to_numpy()
        for cell_id, group in df.groupby("cell_id", sort=True)
    }

    cells = np.array(list(cell_indices))
    events = []
    anomalous_rows = 0
    event_number = 1
    attempts = 0
    max_attempts = 20000

    while anomalous_rows < target_rows and attempts < max_attempts:
        attempts += 1

        # Cycle through anomaly families so all anomaly types are represented.
        anomaly_type = anomaly_types[(event_number - 1) % len(anomaly_types)]
        spec = ANOMALY_SPECS[anomaly_type]

        min_duration, max_duration = spec["duration_intervals"]
        duration = int(rng.integers(min_duration, max_duration + 1))

        cell_id = str(rng.choice(cells))
        indices = cell_indices[cell_id]

        start_pos = int(
            rng.integers(
                0,
                len(indices) - duration + 1,
            )
        )

        end_pos = start_pos + duration
        candidate = indices[start_pos:end_pos]

        guard_start = max(
            0,
            start_pos - EVENT_GUARD_INTERVALS,
        )

        guard_end = min(
            len(indices),
            end_pos + EVENT_GUARD_INTERVALS,
        )

        guard = indices[guard_start:guard_end]

        if df.loc[guard, "is_anomaly"].any():
            continue

        anomaly_id = f"ANOM_{event_number:04d}"

        _apply_anomaly(
            df,
            candidate,
            anomaly_type,
            rng,
        )

        df.loc[candidate, "is_anomaly"] = 1
        df.loc[candidate, "anomaly_type"] = anomaly_type
        df.loc[candidate, "anomaly_id"] = anomaly_id

        start_time = df.loc[candidate[0], "timestamp"]
        end_time = df.loc[candidate[-1], "timestamp"]

        events.append(
            {
                "anomaly_id": anomaly_id,
                "cell_id": cell_id,
                "anomaly_type": anomaly_type,
                "start_time": start_time,
                "end_time": end_time,
                "duration_intervals": duration,
                "duration_minutes": duration * INTERVAL_MINUTES,
            }
        )

        anomalous_rows += duration
        event_number += 1

    if anomalous_rows < target_rows:
        raise RuntimeError(
            "Could not schedule enough non-overlapping anomaly events."
        )

    return df, pd.DataFrame(events)


def save_outputs(
    df: pd.DataFrame,
    manifest: pd.DataFrame,
) -> None:
    """Save full labeled data, GitHub-safe sample, and event manifest."""

    output_path = Path(ANOMALY_OUTPUT_PATH)
    sample_path = Path(ANOMALY_SAMPLE_PATH)
    manifest_path = Path(EVENT_MANIFEST_PATH)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    manifest.to_csv(manifest_path, index=False)

    anomaly_sample = df[df["is_anomaly"] == 1].sample(
        n=min(120, int(df["is_anomaly"].sum())),
        random_state=ANOMALY_SEED,
    )

    normal_sample = df[df["is_anomaly"] == 0].sample(
        n=80,
        random_state=ANOMALY_SEED,
    )

    sample = (
        pd.concat([normal_sample, anomaly_sample])
        .sort_values(["timestamp", "cell_id"])
    )

    sample.to_csv(sample_path, index=False)

    print(f"Full labeled dataset saved to: {output_path}")
    print(f"Labeled sample saved to:       {sample_path}")
    print(f"Event manifest saved to:       {manifest_path}")


def main() -> None:
    normal_path = Path(RAW_OUTPUT_PATH)

    if not normal_path.exists():
        raise FileNotFoundError(
            f"{normal_path} not found. "
            "Run: python -m simulator.generator"
        )

    normal_df = pd.read_csv(
        normal_path,
        parse_dates=["timestamp"],
    )

    df, manifest = inject_anomalies(normal_df)
    save_outputs(df, manifest)

    anomalous_rows = int(df["is_anomaly"].sum())
    anomaly_fraction = anomalous_rows / len(df) * 100

    print()
    print("Controlled anomaly injection completed.")
    print(f"Rows:             {len(df):,}")
    print(f"Anomalous rows:   {anomalous_rows:,}")
    print(f"Anomaly rate:     {anomaly_fraction:.2f}%")
    print(f"Anomaly events:   {len(manifest):,}")

    print()
    print("Rows by anomaly type:")

    print(
        df.loc[
            df["is_anomaly"] == 1,
            "anomaly_type",
        ]
        .value_counts()
        .sort_index()
    )


if __name__ == "__main__":
    main()
