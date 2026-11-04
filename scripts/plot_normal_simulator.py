"""Create targeted visual checks for the normal telecom simulator.

Run after:
    python -m simulator.generator

The figures are saved under:
    docs/figures/normal_simulator/

This script uses Matplotlib's non-interactive "Agg" backend so it does not
depend on Tkinter/Tcl and works reliably from the terminal.
"""

from pathlib import Path

import matplotlib

# IMPORTANT:
# Use a non-interactive backend before importing pyplot.
# This avoids Tkinter/Tcl GUI errors on Windows.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from simulator.config import RAW_OUTPUT_PATH


FIGURE_DIR = Path("docs/figures/normal_simulator")


def save_current_figure(filename: str) -> None:
    """Save the current Matplotlib figure and close it."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    path = FIGURE_DIR / filename

    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()

    print(f"Saved: {path}")


def main() -> None:
    df = pd.read_csv(
        RAW_OUTPUT_PATH,
        parse_dates=["timestamp"],
    )

    df["hour"] = df["timestamp"].dt.hour

    # 1. Daily user pattern by cell personality
    hourly_users = (
        df.groupby(["hour", "location_type"])["connected_users"]
        .mean()
        .unstack()
    )

    plt.figure(figsize=(10, 5))

    for column in hourly_users.columns:
        plt.plot(
            hourly_users.index,
            hourly_users[column],
            marker="o",
            label=column,
        )

    plt.title("Average Connected Users by Hour and Cell Type")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Connected Users")
    plt.xticks(range(0, 24, 2))
    plt.legend()

    save_current_figure(
        "01_hourly_users_by_cell_type.png"
    )

    # 2. User count versus achieved throughput
    sample = df.sample(
        n=min(5000, len(df)),
        random_state=42,
    )

    plt.figure(figsize=(8, 6))

    plt.scatter(
        sample["connected_users"],
        sample["throughput_mbps"],
        alpha=0.25,
    )

    plt.title("Connected Users vs Throughput")
    plt.xlabel("Connected Users")
    plt.ylabel("Throughput (Mbps)")

    save_current_figure(
        "02_users_vs_throughput.png"
    )

    # 3. Normal packet-loss distribution
    plt.figure(figsize=(9, 5))

    plt.hist(
        df["packet_loss_percent"],
        bins=40,
    )

    plt.title("Normal Packet-Loss Distribution")
    plt.xlabel("Packet Loss (%)")
    plt.ylabel("Number of Observations")

    save_current_figure(
        "03_packet_loss_distribution.png"
    )

    # 4. Latency distribution
    plt.figure(figsize=(9, 5))

    plt.hist(
        df["latency_ms"],
        bins=40,
    )

    plt.title("Normal Latency Distribution")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Number of Observations")

    save_current_figure(
        "04_latency_distribution.png"
    )

    # 5. Handover behavior by cell personality
    avg_handover = (
        df.groupby("location_type")["handover_count"]
        .mean()
        .sort_values()
    )

    plt.figure(figsize=(8, 5))

    avg_handover.plot(kind="bar")

    plt.title("Average Handover Count by Cell Type")
    plt.xlabel("Cell Type")
    plt.ylabel("Average Handover Count per 15 Minutes")
    plt.xticks(rotation=30, ha="right")

    save_current_figure(
        "05_handover_by_cell_type.png"
    )

    # 6. Two-day throughput pattern for one cell of each type
    start = df["timestamp"].min()
    end = start + pd.Timedelta(days=2)

    cell_examples = (
        df[["cell_id", "location_type"]]
        .drop_duplicates()
        .drop_duplicates("location_type")
    )

    two_days = df[
        (df["timestamp"] >= start)
        & (df["timestamp"] < end)
    ]

    plt.figure(figsize=(12, 6))

    for row in cell_examples.itertuples(index=False):
        cell_data = two_days[
            two_days["cell_id"] == row.cell_id
        ]

        plt.plot(
            cell_data["timestamp"],
            cell_data["throughput_mbps"],
            label=f"{row.cell_id} ({row.location_type})",
        )

    plt.title(
        "Two-Day Throughput Pattern: Example Cell of Each Type"
    )
    plt.xlabel("Time")
    plt.ylabel("Throughput (Mbps)")
    plt.legend()
    plt.xticks(rotation=30, ha="right")

    save_current_figure(
        "06_example_cell_throughput_2days.png"
    )

    print()
    print("Visual validation figures created successfully.")
    print(f"Figure directory: {FIGURE_DIR.resolve()}")


if __name__ == "__main__":
    main()
