"""Visual validation for injected telecom anomaly events.

Run after:
    python -m simulator.anomaly_injector
    python -m scripts.validate_anomaly_dataset

This script selects one representative event from each anomaly family and
plots the relevant KPIs before, during, and after the event.

Figures are saved under:
    docs/figures/anomaly_validation/
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from simulator.anomaly_config import (
    ANOMALY_OUTPUT_PATH,
    EVENT_MANIFEST_PATH,
)

FIGURE_DIR = Path("docs/figures/anomaly_validation")
CONTEXT_BEFORE = pd.Timedelta(hours=2)
CONTEXT_AFTER = pd.Timedelta(hours=2)

PLOT_CONFIG = {
    "latency_spike": [
        ("latency_ms", "Latency (ms)"),
    ],
    "packet_loss_spike": [
        ("packet_loss_percent", "Packet Loss (%)"),
    ],
    "throughput_degradation": [
        ("throughput_mbps", "Throughput (Mbps)"),
        ("download_traffic_gb", "Download Traffic (GB / 15 min)"),
    ],
    "traffic_surge": [
        ("connected_users", "Connected Users"),
        ("throughput_mbps", "Throughput (Mbps)"),
        ("cpu_usage_percent", "CPU Usage (%)"),
    ],
    "cpu_overload": [
        ("cpu_usage_percent", "CPU Usage (%)"),
    ],
    "memory_overload": [
        ("memory_usage_percent", "Memory Usage (%)"),
    ],
    "multi_kpi_degradation": [
        ("throughput_mbps", "Throughput (Mbps)"),
        ("latency_ms", "Latency (ms)"),
        ("packet_loss_percent", "Packet Loss (%)"),
        ("cpu_usage_percent", "CPU Usage (%)"),
    ],
}

def save_current_figure(filename: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURE_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")

def choose_representative_event(manifest: pd.DataFrame, anomaly_type: str) -> pd.Series:
    events = (
        manifest[manifest["anomaly_type"] == anomaly_type]
        .sort_values("duration_minutes")
        .reset_index(drop=True)
    )
    if events.empty:
        raise ValueError(f"No events found for anomaly type: {anomaly_type}")
    return events.iloc[len(events) // 2]

def plot_event(df: pd.DataFrame, event: pd.Series) -> None:
    anomaly_type = event["anomaly_type"]
    cell_id = event["cell_id"]
    anomaly_id = event["anomaly_id"]
    event_start = event["start_time"]
    event_end = event["end_time"]

    window_start = event_start - CONTEXT_BEFORE
    window_end = event_end + CONTEXT_AFTER

    window = df[
        (df["cell_id"] == cell_id)
        & (df["timestamp"] >= window_start)
        & (df["timestamp"] <= window_end)
    ].copy()

    metrics = PLOT_CONFIG[anomaly_type]

    for metric, ylabel in metrics:
        plt.figure(figsize=(11, 5))
        plt.plot(
            window["timestamp"],
            window[metric],
            marker="o",
            markersize=3,
        )
        plt.axvspan(event_start, event_end, alpha=0.20)
        plt.axvline(event_start, linestyle="--")
        plt.axvline(event_end, linestyle="--")
        plt.title(f"{anomaly_type} | {cell_id} | {anomaly_id}")
        plt.xlabel("Time")
        plt.ylabel(ylabel)
        plt.xticks(rotation=30, ha="right")
        save_current_figure(f"{anomaly_type}__{metric}.png")

def main() -> None:
    data_path = Path(ANOMALY_OUTPUT_PATH)
    manifest_path = Path(EVENT_MANIFEST_PATH)

    if not data_path.exists():
        raise FileNotFoundError(
            f"{data_path} not found. Run: python -m simulator.anomaly_injector"
        )

    if not manifest_path.exists():
        raise FileNotFoundError(f"{manifest_path} not found.")

    df = pd.read_csv(data_path, parse_dates=["timestamp"])
    manifest = pd.read_csv(
        manifest_path,
        parse_dates=["start_time", "end_time"],
    )

    print("=" * 70)
    print("ANOMALY VISUAL VALIDATION")
    print("=" * 70)

    selected_events = []

    for anomaly_type in PLOT_CONFIG:
        event = choose_representative_event(manifest, anomaly_type)

        selected_events.append(
            {
                "anomaly_type": anomaly_type,
                "anomaly_id": event["anomaly_id"],
                "cell_id": event["cell_id"],
                "start_time": event["start_time"],
                "end_time": event["end_time"],
                "duration_minutes": event["duration_minutes"],
            }
        )

        print(
            f"{anomaly_type:26s} "
            f"{event['anomaly_id']} "
            f"{event['cell_id']} "
            f"{int(event['duration_minutes'])} min"
        )

        plot_event(df, event)

    selected = pd.DataFrame(selected_events)
    selected_path = FIGURE_DIR / "selected_anomaly_events.csv"
    selected.to_csv(selected_path, index=False)

    print()
    print("Visual validation figures created successfully.")
    print(f"Figure directory: {FIGURE_DIR.resolve()}")

if __name__ == "__main__":
    main()
