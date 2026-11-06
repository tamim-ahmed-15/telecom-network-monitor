# Step 12 — Visual Validation of Injected Anomalies

## Goal

Verify that every injected anomaly family looks meaningfully different from
the surrounding normal behavior before uploading the labeled synthetic
dataset to Kaggle.

This step validates the **shape and context** of anomaly events, not just
their labels.

## Anomaly Families

```text
latency_spike
packet_loss_spike
throughput_degradation
traffic_surge
cpu_overload
memory_overload
multi_kpi_degradation
```

## Validation Principle

Each event should be inspected with normal observations before and after it.

Example:

```text
Normal
Normal
Normal
ANOMALY
ANOMALY
ANOMALY
Normal
Normal
```

A correct anomaly should be visible relative to its local baseline.

## Expected Visual Patterns

### latency_spike

```text
latency_ms ↑ sharply
```

### packet_loss_spike

```text
packet_loss_percent ↑ sharply
```

### throughput_degradation

```text
throughput_mbps ↓
download_traffic_gb ↓
```

### traffic_surge

```text
connected_users ↑
throughput_mbps ↑
cpu_usage_percent ↑
```

with only mild latency / packet-loss degradation.

### cpu_overload

```text
cpu_usage_percent → approximately 90–99%
```

without automatically forcing every other KPI to fail.

### memory_overload

```text
memory_usage_percent → approximately 90–99%
```

and the event should usually last longer than a one-interval spike.

### multi_kpi_degradation

```text
throughput_mbps ↓
latency_ms ↑
packet_loss_percent ↑
cpu_usage_percent ↑
```

This should visually look stronger than a single-KPI anomaly.

## Important Rule

Visual validation is not proof of a physical root cause.

The plots only confirm that controlled KPI patterns were injected correctly.

## Completion Condition

Step 12 is complete when:

- one representative event from every anomaly family has been inspected,
- the anomaly interval is clearly visible relative to surrounding normal data,
- no anomaly family looks identical to another,
- no event produces impossible KPI values,
- the original normal dataset remains unchanged,
- and the labeled dataset is ready for Kaggle.
