"""Configuration for the Version 1 normal telecom simulator.

All values in this file are simulation assumptions unless explicitly noted
otherwise in docs/step_09_simulator_assumptions.md.
"""

SEED = 42

START_DATE = "2026-01-01 00:00:00"
DAYS = 14
INTERVAL_MINUTES = 15
TECHNOLOGY = "5G"

REGIONS = {
    "Chattogram": "CTG",
    "Dhaka": "DHA",
    "Sylhet": "SYL",
    "Rajshahi": "RAJ",
}

LOCATION_TYPES = [
    "Residential",
    "Business",
    "University",
    "Transport",
    "Suburban",
]

# Approximate per-location-type baselines.
# These are engineering assumptions for the simulator, not operator data.
CELL_PROFILES = {
    "Residential": {
        "user_capacity": 520,
        "capacity_mbps": 90,
        "baseline_latency_ms": 34,
        "baseline_signal_dbm": -82,
        "base_cpu_percent": 24,
        "base_memory_percent": 44,
        "per_user_mbps": 0.115,
        "handover_base": 12,
    },
    "Business": {
        "user_capacity": 480,
        "capacity_mbps": 100,
        "baseline_latency_ms": 28,
        "baseline_signal_dbm": -78,
        "base_cpu_percent": 22,
        "base_memory_percent": 42,
        "per_user_mbps": 0.105,
        "handover_base": 18,
    },
    "University": {
        "user_capacity": 650,
        "capacity_mbps": 110,
        "baseline_latency_ms": 30,
        "baseline_signal_dbm": -80,
        "base_cpu_percent": 24,
        "base_memory_percent": 46,
        "per_user_mbps": 0.110,
        "handover_base": 22,
    },
    "Transport": {
        "user_capacity": 580,
        "capacity_mbps": 95,
        "baseline_latency_ms": 38,
        "baseline_signal_dbm": -86,
        "base_cpu_percent": 26,
        "base_memory_percent": 48,
        "per_user_mbps": 0.095,
        "handover_base": 45,
    },
    "Suburban": {
        "user_capacity": 360,
        "capacity_mbps": 80,
        "baseline_latency_ms": 40,
        "baseline_signal_dbm": -90,
        "base_cpu_percent": 23,
        "base_memory_percent": 43,
        "per_user_mbps": 0.100,
        "handover_base": 8,
    },
}

UPLOAD_RATIO_RANGE = (0.15, 0.30)

RAW_OUTPUT_PATH = "data/raw/telecom_network_normal.csv"
SAMPLE_OUTPUT_PATH = "data/sample/telecom_network_normal_sample.csv"
SAMPLE_ROWS = 200
