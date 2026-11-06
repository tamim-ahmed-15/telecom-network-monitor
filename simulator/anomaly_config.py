"""Configuration for controlled anomaly injection in Version 1."""

ANOMALY_SEED = 2026

# Target approximately 3% anomalous rows in the final labeled dataset.
TARGET_ANOMALY_FRACTION = 0.03

# Keep a small gap between events on the same cell so two different
# anomaly events do not merge visually or operationally.
EVENT_GUARD_INTERVALS = 2

ANOMALY_SPECS = {
    "latency_spike": {
        "duration_intervals": (1, 4),
    },
    "packet_loss_spike": {
        "duration_intervals": (1, 4),
    },
    "throughput_degradation": {
        "duration_intervals": (2, 6),
    },
    "traffic_surge": {
        "duration_intervals": (2, 6),
    },
    "cpu_overload": {
        "duration_intervals": (2, 8),
    },
    "memory_overload": {
        "duration_intervals": (4, 12),
    },
    "multi_kpi_degradation": {
        "duration_intervals": (4, 12),
    },
}

ANOMALY_OUTPUT_PATH = "data/raw/telecom_network_raw.csv"
ANOMALY_SAMPLE_PATH = "data/sample/telecom_network_labeled_sample.csv"
EVENT_MANIFEST_PATH = "data/sample/anomaly_event_manifest.csv"
