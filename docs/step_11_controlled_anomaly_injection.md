# Step 11 — Controlled Anomaly Injection

## Goal

Create a labeled anomaly dataset from the validated normal telecom simulator
without modifying the original normal dataset.

The final dataset should contain approximately 3% anomalous rows distributed
across seven controlled anomaly families.

## Files

```text
simulator/
├── anomaly_config.py
└── anomaly_injector.py

scripts/
└── validate_anomaly_dataset.py
```

Generated outputs:

```text
data/raw/
└── telecom_network_raw.csv

data/sample/
├── telecom_network_labeled_sample.csv
└── anomaly_event_manifest.csv
```

## Frozen Anomaly Families

```text
latency_spike
packet_loss_spike
throughput_degradation
traffic_surge
cpu_overload
memory_overload
multi_kpi_degradation
```

## Event-Based Design

Anomalies are injected as contiguous events rather than independent random
rows.

Example:

```text
Normal
Normal
ANOM_0001
ANOM_0001
ANOM_0001
Normal
Normal
```

Each event has:

```text
anomaly_id
cell_id
anomaly_type
start_time
end_time
duration_intervals
duration_minutes
```

The event manifest is preserved for later evaluation of persistence and
detection delay.

## Labels

Normal rows:

```text
is_anomaly = 0
anomaly_type = normal
anomaly_id = empty
```

Injected rows:

```text
is_anomaly = 1
anomaly_type = <scenario>
anomaly_id = ANOM_XXXX
```

Ground-truth labels are reserved for evaluation and must not be supplied as
Isolation Forest input features.

## Validation Requirements

The final dataset must preserve:

- 26,880 rows
- 20 cells
- no duplicate rows
- valid KPI ranges
- approximately 3% anomaly prevalence
- all seven anomaly types
- contiguous timestamps within each anomaly event
- one cell and one anomaly type per `anomaly_id`

## Important Rule

The anomaly injector describes observable KPI patterns.

It does not claim physical root causes.

For example:

```text
latency ↑
packet loss ↑
throughput ↓
```

may be described as a multi-KPI degradation pattern.

It must not automatically be labeled:

```text
antenna failure
```

without evidence.
