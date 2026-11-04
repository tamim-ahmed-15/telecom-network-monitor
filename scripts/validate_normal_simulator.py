"""Validate the Version 1 normal telecom simulator output."""

from pathlib import Path

import pandas as pd

from simulator.config import (
    DAYS,
    INTERVAL_MINUTES,
    LOCATION_TYPES,
    RAW_OUTPUT_PATH,
    REGIONS,
)


EXPECTED_ROWS = (
    len(REGIONS)
    * len(LOCATION_TYPES)
    * DAYS
    * 24
    * (60 // INTERVAL_MINUTES)
)


def main() -> None:
    path = Path(RAW_OUTPUT_PATH)

    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run: python -m simulator.generator"
        )

    df = pd.read_csv(path, parse_dates=["timestamp"])

    print("=" * 65)
    print("NORMAL TELECOM SIMULATOR VALIDATION")
    print("=" * 65)

    print(f"Rows:              {len(df):,} / expected {EXPECTED_ROWS:,}")
    print(f"Columns:           {len(df.columns)}")
    print(f"Cells:             {df['cell_id'].nunique()}")
    print(f"Regions:           {df['region'].nunique()}")
    print(f"Location types:    {df['location_type'].nunique()}")
    print(f"Duplicate rows:    {df.duplicated().sum()}")
    print(f"Missing values:    {int(df.isna().sum().sum() - df['anomaly_id'].isna().sum())}")
    print(f"Anomalous rows:    {df['is_anomaly'].sum()}")

    print("\nTimestamp range")
    print("Start:", df["timestamp"].min())
    print("End:  ", df["timestamp"].max())

    numeric = [
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
    ]

    print("\nKPI summary")
    print(
        df[numeric]
        .describe(percentiles=[0.05, 0.50, 0.95])
        .T[["min", "5%", "50%", "95%", "max"]]
        .round(3)
    )

    df["hour"] = df["timestamp"].dt.hour

    print("\nAverage connected users by cell type at selected hours")
    selected_hours = [2, 8, 13, 18, 20, 22]

    hourly_users = (
        df[df["hour"].isin(selected_hours)]
        .groupby(["hour", "location_type"])["connected_users"]
        .mean()
        .unstack()
        .round(1)
    )

    print(hourly_users)

    print("\nSelected Spearman correlations")
    correlation_columns = [
        "connected_users",
        "download_traffic_gb",
        "throughput_mbps",
        "latency_ms",
        "packet_loss_percent",
        "cpu_usage_percent",
    ]

    print(
        df[correlation_columns]
        .corr(method="spearman")
        .round(2)
    )

    checks = {
        "expected row count": len(df) == EXPECTED_ROWS,
        "20 unique cells": df["cell_id"].nunique() == 20,
        "no duplicate rows": df.duplicated().sum() == 0,
        "all rows normal": df["is_anomaly"].eq(0).all(),
        "anomaly_type is normal": df["anomaly_type"].eq("normal").all(),
        "packet loss non-negative": df["packet_loss_percent"].ge(0).all(),
        "CPU in 0-100": df["cpu_usage_percent"].between(0, 100).all(),
        "memory in 0-100": df["memory_usage_percent"].between(0, 100).all(),
        "throughput non-negative": df["throughput_mbps"].ge(0).all(),
        "latency positive": df["latency_ms"].gt(0).all(),
    }

    print("\nValidation checks")
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if not all(checks.values()):
        raise SystemExit("\nValidation failed.")

    print("\nAll structural validation checks passed.")


if __name__ == "__main__":
    main()
