"""Validate the controlled anomaly dataset."""

from pathlib import Path

import pandas as pd

from simulator.anomaly_config import (
    ANOMALY_OUTPUT_PATH,
    ANOMALY_SPECS,
    EVENT_MANIFEST_PATH,
    TARGET_ANOMALY_FRACTION,
)
from simulator.config import (
    DAYS,
    INTERVAL_MINUTES,
    LOCATION_TYPES,
    REGIONS,
)


EXPECTED_ROWS = (
    len(REGIONS)
    * len(LOCATION_TYPES)
    * DAYS
    * 24
    * (60 // INTERVAL_MINUTES)
)


def _events_are_contiguous(
    df: pd.DataFrame,
) -> bool:
    """Verify that every anomaly ID represents one contiguous cell event."""

    anomaly_rows = df[df["is_anomaly"] == 1]

    for _, group in anomaly_rows.groupby("anomaly_id"):
        group = group.sort_values("timestamp")

        if group["cell_id"].nunique() != 1:
            return False

        if group["anomaly_type"].nunique() != 1:
            return False

        differences = (
            group["timestamp"]
            .diff()
            .dropna()
        )

        if not differences.eq(
            pd.Timedelta(minutes=INTERVAL_MINUTES)
        ).all():
            return False

    return True


def main() -> None:
    data_path = Path(ANOMALY_OUTPUT_PATH)
    manifest_path = Path(EVENT_MANIFEST_PATH)

    if not data_path.exists():
        raise FileNotFoundError(
            f"{data_path} not found. "
            "Run: python -m simulator.anomaly_injector"
        )

    if not manifest_path.exists():
        raise FileNotFoundError(
            f"{manifest_path} not found."
        )

    df = pd.read_csv(
        data_path,
        parse_dates=["timestamp"],
    )

    manifest = pd.read_csv(
        manifest_path,
        parse_dates=["start_time", "end_time"],
    )

    anomaly_rows = df[df["is_anomaly"] == 1].copy()
    normal_rows = df[df["is_anomaly"] == 0].copy()

    anomaly_rate = len(anomaly_rows) / len(df)

    print("=" * 70)
    print("CONTROLLED ANOMALY DATASET VALIDATION")
    print("=" * 70)

    print(
        f"Rows:            {len(df):,} / expected {EXPECTED_ROWS:,}"
    )
    print(f"Columns:         {len(df.columns)}")
    print(f"Cells:           {df['cell_id'].nunique()}")
    print(f"Duplicate rows:  {df.duplicated().sum()}")
    print(f"Anomalous rows:  {len(anomaly_rows):,}")
    print(f"Normal rows:     {len(normal_rows):,}")
    print(f"Anomaly rate:    {anomaly_rate * 100:.2f}%")
    print(
        f"Anomaly events:  "
        f"{manifest['anomaly_id'].nunique():,}"
    )

    print("\nAnomaly rows and events by type")

    rows_by_type = (
        anomaly_rows["anomaly_type"]
        .value_counts()
        .sort_index()
    )

    events_by_type = (
        manifest["anomaly_type"]
        .value_counts()
        .sort_index()
    )

    summary = pd.DataFrame(
        {
            "rows": rows_by_type,
            "events": events_by_type,
        }
    ).fillna(0).astype(int)

    print(summary)

    print("\nEvent duration summary (minutes)")

    print(
        manifest.groupby("anomaly_type")[
            "duration_minutes"
        ]
        .agg(["min", "median", "max"])
        .round(1)
    )

    print("\nNormal vs anomaly KPI medians")

    kpis = [
        "connected_users",
        "download_traffic_gb",
        "upload_traffic_gb",
        "throughput_mbps",
        "latency_ms",
        "packet_loss_percent",
        "cpu_usage_percent",
        "memory_usage_percent",
    ]

    median_table = pd.DataFrame(
        {
            "normal_median": normal_rows[kpis].median(),
            "anomaly_median": anomaly_rows[kpis].median(),
        }
    ).round(3)

    print(median_table)

    expected_types = set(ANOMALY_SPECS)
    actual_types = set(
        anomaly_rows["anomaly_type"].unique()
    )

    allowed_min_rate = (
        TARGET_ANOMALY_FRACTION - 0.005
    )

    allowed_max_rate = (
        TARGET_ANOMALY_FRACTION + 0.005
    )

    checks = {
        "expected row count":
            len(df) == EXPECTED_ROWS,

        "20 unique cells":
            df["cell_id"].nunique() == 20,

        "no duplicate rows":
            df.duplicated().sum() == 0,

        "all 7 anomaly types present":
            actual_types == expected_types,

        "anomaly rate near target":
            allowed_min_rate
            <= anomaly_rate
            <= allowed_max_rate,

        "normal rows labeled normal":
            normal_rows["anomaly_type"]
            .eq("normal")
            .all(),

        "normal anomaly_id empty":
            normal_rows["anomaly_id"]
            .isna()
            .all(),

        "anomaly IDs present":
            anomaly_rows["anomaly_id"]
            .notna()
            .all(),

        "events contiguous":
            _events_are_contiguous(df),

        "packet loss within 0-100":
            df["packet_loss_percent"]
            .between(0, 100)
            .all(),

        "CPU within 0-100":
            df["cpu_usage_percent"]
            .between(0, 100)
            .all(),

        "memory within 0-100":
            df["memory_usage_percent"]
            .between(0, 100)
            .all(),

        "throughput positive":
            df["throughput_mbps"]
            .gt(0)
            .all(),

        "latency positive":
            df["latency_ms"]
            .gt(0)
            .all(),

        "users positive":
            df["connected_users"]
            .gt(0)
            .all(),
    }

    print("\nValidation checks")

    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")

    if not all(checks.values()):
        raise SystemExit(
            "\nValidation failed."
        )

    print(
        "\nAll anomaly-dataset validation checks passed."
    )


if __name__ == "__main__":
    main()
