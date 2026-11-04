# Step 9 — Design the Synthetic NOC Dataset and Simulator Assumptions

## Telecom Network Monitoring & Anomaly Detection System

## Goal

Step 9 converts the real RANalyzer EDA findings into a clear, documented
design for the synthetic multi-cell telecom dataset.

We are **not coding the simulator yet**.

The purpose of this step is to freeze:

- the simulated network size,
- the measurement interval,
- the final dataset schema,
- which assumptions are real-data-informed,
- which assumptions are purely synthetic,
- how normal KPI relationships should behave,
- and how anomaly scenarios should be defined.

This prevents us from inventing arbitrary numbers later while writing code.

---

# 1. Step 8 Findings That Influence the Simulator

The RANalyzer analysis produced several important observations.

## 1.1 Offered load and achieved throughput are strongly related

The Spearman correlation between:

```text
target_rate_mbps
and
avg_throughput_mbps
```

was approximately:

```text
0.96
```

This is a very strong positive association.

The test-rate summary also showed that throughput generally stayed close to
the requested rate under ordinary operation.

Examples:

| Target Rate | Median Throughput | Median Efficiency |
|---:|---:|---:|
| 10 Mbps | 10.00 Mbps | 100.00% |
| 20 Mbps | 19.98 Mbps | 99.90% |
| 30 Mbps | 29.88 Mbps | 99.59% |
| 50 Mbps | 49.76 Mbps | 99.52% |
| 60 Mbps | 59.59 Mbps | 99.31% |

Therefore the synthetic simulator should preserve the idea:

```text
Demand / Offered Load
        ↓
Achieved Throughput Usually Follows Demand
        ↓
Until Capacity / Degradation Effects Become Important
```

This relationship is **real-data-informed**.

---

# 2. Throughput Efficiency Findings

The observed throughput-efficiency percentiles were:

```text
1st percentile    ≈ 46.52%
5th percentile    ≈ 86.24%
10th percentile   ≈ 97.48%
25th percentile   ≈ 99.35%
Median            ≈ 99.87%
75th percentile   ≈ 100.00%
```

This means most RANalyzer tests achieved throughput very close to the
configured target rate.

Only a relatively small tail exhibited major degradation.

There were:

```text
102 runs
```

with throughput efficiency below:

```text
50%
```

out of 8,611 test runs.

Therefore Version 1 should model **normal throughput as stable and efficient**,
while major throughput loss should mainly appear during anomalies or severe
load conditions.

---

# 3. Packet-Loss Findings

Observed packet-loss percentiles were:

```text
50th percentile   = 0.00%
75th percentile   = 0.21%
90th percentile   = 0.86%
95th percentile   = 1.865%
99th percentile   = 5.368%
99.5th percentile = 12.833%
Maximum           = 96.15%
```

The dataset therefore has a strongly right-skewed packet-loss distribution.

Most measurements have:

```text
very low packet loss
```

while a small number have:

```text
very high packet loss
```

There were:

```text
51 runs
```

with packet loss greater than or equal to:

```text
10%
```

Therefore the simulator should **not** generate packet loss using a symmetric
normal distribution.

Instead, packet loss should usually remain near zero with a small positive
tail.

This behavior is **real-data-informed**.

---

# 4. Jitter Findings

Observed jitter percentiles were:

```text
50th percentile   ≈ 0.162 ms
75th percentile   ≈ 0.295 ms
90th percentile   ≈ 0.798 ms
95th percentile   ≈ 1.595 ms
99th percentile   ≈ 2.102 ms
99.5th percentile ≈ 2.759 ms
Maximum           ≈ 46.064 ms
```

Only:

```text
4 runs
```

had average jitter greater than or equal to:

```text
5 ms
```

This confirms a long-tailed behavior.

Jitter is useful for understanding the real data, but it is **not required as
a core Version 1 NOC field**.

We will therefore keep jitter out of the first synthetic dataset unless later
needed.

---

# 5. Offered Load and Performance Degradation

As target rate increased, efficiency generally became less stable.

Examples:

| Target Rate | Mean Efficiency | Mean Packet Loss |
|---:|---:|---:|
| 10 Mbps | 99.47% | 0.22% |
| 20 Mbps | 98.50% | 0.27% |
| 30 Mbps | 97.26% | 0.48% |
| 50 Mbps | 98.02% | 0.27% |
| 60 Mbps | 96.00% | 0.69% |
| 70 Mbps | 87.85% | 1.94% |
| 80 Mbps | 85.09% | 14.45% |
| 90 Mbps | 82.32% | 17.20% |

However, the number of tests at the highest rates was very small:

```text
75 Mbps → 3 tests
80 Mbps → 5 tests
90 Mbps → 1 test
```

Therefore we should **not** treat those high-rate averages as universal
thresholds.

The safe conclusion is only:

```text
Higher Offered Load
        ↓
Can Increase Performance Pressure
        ↓
Efficiency May Fall
Packet Loss May Increase
```

This relationship will be implemented as a **soft load effect**, not a fixed
rule.

---

# 6. Important Confounding Observation

The Spearman correlations included:

```text
Target Rate ↔ Throughput       = +0.96

Target Rate ↔ Packet Loss      = +0.45

Throughput ↔ Packet Loss       = +0.33

Efficiency ↔ Packet Loss       = -0.69
```

The positive correlation between raw throughput and packet loss should **not**
be interpreted as:

```text
Higher Throughput Causes Packet Loss
```

A more sensible interpretation is that higher target rates simultaneously:

```text
increase achieved throughput
and
increase network stress
```

This creates a confounding relationship.

Therefore our simulator should model:

```text
Offered Load
   ├──→ Throughput Demand
   └──→ Network Stress
              ↓
      Packet Loss / Efficiency
```

rather than directly making packet loss a function of throughput alone.

---

# 7. Radio-Signal Findings

The correlations between `avg_rsrp` / `avg_snr` and achieved throughput were
very weak in this dataset.

Approximately:

```text
RSRP ↔ Throughput ≈ -0.01
SNR  ↔ Throughput ≈ -0.06
```

This means RANalyzer does **not** provide strong evidence for a simple direct
relationship such as:

```text
Better RSRP
     ↓
Higher Throughput
```

within this particular test environment.

In addition, 60 records had:

```text
avg_rsrp >= -20 dBm
```

including values close to:

```text
-1 dBm
```

and the original summary included values up to:

```text
0 dBm
```

These values should not be used blindly as realistic cellular-signal
calibration values.

Therefore:

> Version 1 will treat signal quality as a synthetic contextual KPI rather
> than using the raw RANalyzer RSRP distribution directly.

The simulator may include a mild relationship between poor signal conditions
and performance, but it must not make signal quality the dominant driver.

---

# 8. Missing SNR Is Systematic

RANalyzer contains:

```text
1,975 rows
```

with missing SNR values:

```text
22.94%
```

The missingness is strongly associated with particular `git_hash` software
releases.

Some releases have SNR for all tests, while others have SNR missing for every
test.

Therefore:

```text
Missing SNR is not random.
```

We should not interpret those missing values as poor signal.

For our synthetic simulator, Version 1 will initially generate complete
signal-quality data rather than reproducing RANalyzer's software-version
logging gaps.

Data-quality corruption can be added separately later when testing the
preprocessing pipeline.

---

# 9. BLER and HARQ Findings

Average BLER statistics:

```text
DL BLER median ≈ 0.069
UL BLER median ≈ 0.034
```

The retransmission ratios showed:

```text
DL BLER ↔ DL retransmission ratio ≈ +0.47

UL BLER ↔ UL retransmission ratio ≈ +0.80
```

These relationships are technically useful and support the interpretation
of the radio-reliability features.

However, BLER and HARQ are not required for the first NOC application.

Therefore Version 1 will **not include BLER/HARQ as primary synthetic KPIs**.

They remain candidates for Version 2.

---

# 10. Software-Version Effects

The real dataset contains:

```text
65 git_hash values
```

and performance differs across software releases.

For example, some releases showed mean efficiency near:

```text
99–100%
```

while others were closer to:

```text
92–95%
```

The runs with extremely low throughput efficiency were also concentrated in
some software versions.

Therefore extreme RANalyzer performance should **not automatically be treated
as generic network congestion**.

Some degradation may represent software regression or testbed behavior.

For our simulator, we will reproduce the **observable KPI degradation
patterns**, not claim the same root cause.

---

# 11. Large `total_bytes` Values Are Not Anomalies by Themselves

Most RANalyzer tests lasted:

```text
10 seconds
```

but some lasted:

```text
60 seconds
600 seconds
```

The largest `total_bytes` values were associated with 600-second tests.

Therefore:

```text
large total_bytes
```

does not automatically mean:

```text
abnormal traffic
```

because volume depends strongly on duration.

Our synthetic NOC dataset will use a fixed:

```text
15-minute measurement interval
```

which makes traffic-volume comparisons much easier.

---

# 12. Final Version 1 Synthetic Network Size

We will generate:

```text
20 cells

14 days

15-minute intervals
```

Number of intervals per day:

```text
24 × 4 = 96
```

Intervals per cell:

```text
14 × 96 = 1,344
```

Total measurements:

```text
20 × 1,344 = 26,880 rows
```

Expected dataset shape before derived features:

```text
approximately 26,880 rows
```

---

# 13. Simulated Regions and Cells

The 20 cells will be explicitly synthetic.

Use four regional labels:

```text
Chattogram
Dhaka
Sylhet
Rajshahi
```

Each region will contain five cells.

Example:

```text
CTG_001 – CTG_005

DHA_001 – DHA_005

SYL_001 – SYL_005

RAJ_001 – RAJ_005
```

These IDs do **not** represent real operator cells.

---

# 14. Cell Types

Each region will contain one cell of each type:

```text
Residential

Business

University

Transport

Suburban
```

Therefore:

```text
4 regions
×
5 cell types
=
20 cells
```

This gives a balanced and easy-to-understand Version 1 network.

---

# 15. Technology

Version 1 will use:

```text
technology = "5G"
```

for all simulated cells.

Reason:

The real reference dataset is a 5G dataset.

Keeping one technology simplifies Version 1 and avoids inventing artificial
4G/5G differences.

Support for multiple technologies can be added later.

---

# 16. Final Raw Dataset Schema

The initial synthetic dataset will contain:

```text
timestamp

cell_id
region
location_type
technology

connected_users

download_traffic_gb
upload_traffic_gb

throughput_mbps
latency_ms
packet_loss_percent

signal_quality_dbm

cpu_usage_percent
memory_usage_percent

handover_count

is_anomaly
anomaly_type
anomaly_id
```

The explicit units in column names reduce ambiguity.

---

# 17. Metadata Fields

## `timestamp`

One observation every:

```text
15 minutes
```

for 14 days.

---

## `cell_id`

Synthetic identifier.

Example:

```text
CTG_001
```

---

## `region`

One of:

```text
Chattogram
Dhaka
Sylhet
Rajshahi
```

---

## `location_type`

One of:

```text
Residential
Business
University
Transport
Suburban
```

---

## `technology`

Always:

```text
5G
```

in Version 1.

---

# 18. Connected Users

`connected_users` is **fully synthetic** because the processed RANalyzer data
does not contain a suitable multi-cell connected-user KPI.

Each cell will have its own:

```text
user_capacity
```

configuration.

For simplicity, Version 1 can assign capacities approximately within:

```text
250–700 users
```

depending on the cell.

This is an engineering assumption, **not a value derived from RANalyzer**.

Actual active-user counts will depend on:

```text
Cell capacity
+
Location type
+
Time of day
+
Day of week
+
Natural random variation
```

---

# 19. Daily Usage Profiles

## Residential

Expected pattern:

```text
00:00–06:00 → Low

07:00–09:00 → Increasing

10:00–16:00 → Moderate

17:00–23:00 → High
```

Main peak:

```text
Evening
```

---

## Business

Expected pattern:

```text
00:00–06:00 → Very low

07:00–09:00 → Increasing

09:00–17:00 → High

18:00–23:00 → Low
```

Main peak:

```text
Office hours
```

---

## University

Expected pattern:

```text
Morning → Increasing

09:00–17:00 → High

Evening → Moderate/low

Night → Low
```

---

## Transport

Use two daily peaks:

```text
07:00–10:00
and
17:00–20:00
```

This represents commuting periods.

---

## Suburban

Use:

```text
Low/moderate daytime activity
+
moderate evening peak
```

These profiles are **synthetic behavioral assumptions**, not extracted from
RANalyzer.

---

# 20. Weekend Effect

Add a small weekend effect.

Example:

```text
Business cells
→ lower weekend load

University cells
→ lower weekend load

Residential cells
→ slightly higher daytime weekend activity
```

Do not make weekend effects extreme.

---

# 21. Network Load Variable

The simulator should internally calculate a normalized variable:

```text
load_ratio
```

Conceptually:

```text
load_ratio ≈ current demand / cell capacity
```

Typical range:

```text
0.0–1.0
```

Temporary overload scenarios may exceed:

```text
1.0
```

before clipping or congestion effects are applied.

`load_ratio` does not necessarily have to appear in the final user-facing
dataset, but it is useful inside the simulator.

---

# 22. Download and Upload Traffic

Traffic-volume fields are synthetic:

```text
download_traffic_gb

upload_traffic_gb
```

per 15-minute interval.

Traffic should depend primarily on:

```text
connected_users
+
location_type
+
time of day
+
random user activity
```

Conceptually:

```text
Connected Users ↑
        ↓
Aggregate Traffic Demand ↑
```

Upload traffic should generally be lower than download traffic in Version 1.

A simple first assumption is:

```text
upload traffic
≈
15–30% of download traffic
```

with natural variation.

This is a simulator assumption, not a RANalyzer-derived rule.

---

# 23. Throughput

Throughput is **real-data-informed**.

RANalyzer shows that achieved throughput generally follows offered load very
closely under normal operation.

Therefore:

```text
normal throughput
=
demand-driven throughput
×
normal efficiency factor
```

Normal efficiency should usually remain close to:

```text
97.5–100%
```

of the achievable/requested level.

Do not allow every cell to have identical throughput.

Each cell should have its own synthetic:

```text
capacity_mbps
```

For Version 1, reasonable synthetic capacity values can be assigned within a
range such as:

```text
70–110 Mbps
```

This capacity range is an **engineering assumption**, not a direct claim from
RANalyzer.

---

# 24. Soft Capacity Saturation

Throughput should not increase infinitely.

As demand approaches cell capacity:

```text
Load ↑
    ↓
Available headroom ↓
    ↓
Efficiency can decrease
```

The simulator should therefore use a soft saturation effect.

Conceptually:

```text
Low Load
→ Throughput comfortably follows demand

Medium Load
→ Throughput follows demand

High Load
→ Throughput approaches capacity

Very High Load
→ Efficiency decreases
```

Do not use a hard cliff.

---

# 25. Packet Loss

Packet loss is **real-data-informed**.

RANalyzer shows:

```text
median = 0%

75% of tests ≤ 0.21%

90% of tests ≤ 0.86%

95% of tests ≤ 1.865%
```

Therefore normal Version 1 behavior should usually remain:

```text
0–1%
```

with occasional mild values up to approximately:

```text
1–2%
```

before anomaly injection.

Do not generate normal packet loss using a symmetric Gaussian centered well
above zero.

Use a **zero-heavy / right-skewed** distribution.

Example design:

```text
~50–60% of normal samples
→ exactly or almost 0%

Most remaining normal samples
→ 0.01–0.8%

Small natural tail
→ 0.8–1.8%
```

These percentages are simulator design choices guided by the observed
RANalyzer percentiles.

---

# 26. Latency

Latency is **fully synthetic in Version 1** because the processed RANalyzer
file does not provide a direct latency field.

Each cell should receive its own baseline latency.

Example engineering assumption:

```text
baseline latency
≈ 25–45 ms
```

Natural variation can move it around the baseline.

Load can have a mild effect:

```text
Low/medium load
→ latency near baseline

High load
→ latency gradually increases
```

Latency should not jump dramatically during normal operation.

Large increases will be injected as anomalies.

---

# 27. Signal Quality

Version 1 will represent signal quality as:

```text
signal_quality_dbm
```

using an RSRP-like synthetic value.

Because the RANalyzer RSRP distribution contains suspicious values and shows
little direct relationship with performance, the raw RANalyzer distribution
will **not** be copied.

Each cell should have a stable baseline signal level.

A simple synthetic engineering range can be:

```text
approximately -95 to -75 dBm baseline
```

with small natural fluctuations.

This is an explicit simulation assumption.

Signal quality should have only a **mild influence** on performance in V1.

---

# 28. CPU Usage

CPU utilization is synthetic in the processed Version 1 dataset.

It should depend partly on network load.

Conceptually:

```text
Load ↑
   ↓
CPU Usage ↑
```

Normal CPU behavior can generally remain within:

```text
20–80%
```

with cell-specific variation.

A simple model:

```text
base CPU
+
load-dependent component
+
noise
```

CPU overload anomalies will intentionally push CPU much higher.

---

# 29. Memory Usage

Memory usage is also synthetic.

Memory should vary more slowly than CPU.

Normal range can generally remain around:

```text
30–80%
```

with small changes over time.

Unlike CPU, memory should not strongly jump every 15 minutes during normal
operation.

---

# 30. Handover Count

`handover_count` is synthetic in Version 1.

Expected relative behavior:

```text
Transport
→ highest handover activity

University / Business
→ medium

Residential
→ low/medium

Suburban
→ generally lower
```

Example synthetic ranges per 15-minute interval:

```text
Residential   → 5–25

Business      → 10–35

University    → 10–40

Transport     → 25–80

Suburban      → 3–20
```

These are simulator assumptions, not measured RANalyzer values.

---

# 31. Natural Random Variation

No KPI should be perfectly smooth.

For example:

```text
Latency:

34
36
35
38
33
```

rather than:

```text
35
35
35
35
35
```

However random noise must remain small enough that the daily patterns and KPI
relationships are still visible.

---

# 32. Normal KPI Relationship Graph

The simulator should approximately follow:

```text
               Time of Day
                   │
                   ▼
             User Activity
                   │
                   ▼
            Connected Users
                   │
                   ▼
             Traffic Demand
                   │
                   ▼
              Load Ratio
           ┌───────┼─────────┐
           ▼       ▼         ▼
          CPU   Throughput  Latency
                   │
                   ▼
           Capacity Pressure
                   │
                   ▼
             Packet Loss
```

Signal quality acts as a smaller contextual influence.

Memory changes partly with system load but more slowly.

Handover count depends primarily on cell type and mobility pattern.

---

# 33. What We Must NOT Encode

Do not create deterministic rules such as:

```text
High Users
=
Packet Loss
```

or:

```text
Poor RSRP
=
Low Throughput
```

Instead use probabilistic relationships:

```text
Higher Load
→ higher probability of mild degradation
```

This produces more realistic overlapping normal behavior.

---

# 34. Ground-Truth Anomaly Prevalence

Version 1 should keep anomalies rare.

Initial target:

```text
approximately 2–4% of rows
```

should belong to injected anomaly periods.

Do not force exactly 3%.

The final rate should be reported after generation.

This keeps:

```text
Normal observations
≫
Anomalous observations
```

which is appropriate for anomaly detection.

---

# 35. Anomaly Type 1 — Latency Spike

Normal:

```text
approximately 25–45 ms baseline
+
small natural load variation
```

Anomaly:

```text
latency × 3–6
```

or otherwise push it substantially above the cell's own baseline.

Duration:

```text
1–4 intervals
```

for a short event.

---

# 36. Anomaly Type 2 — Packet-Loss Spike

Normal:

```text
usually 0–1%
```

Anomalous range can approximately use:

```text
5–20%
```

The real RANalyzer data confirms that values above 10% occur but are rare.

Some severe anomaly events may exceed 20%, but they should be uncommon.

---

# 37. Anomaly Type 3 — Throughput Degradation

The RANalyzer dataset contains 102 runs with less than 50% throughput
efficiency.

Therefore a strong synthetic throughput-degradation anomaly can reduce
throughput by approximately:

```text
40–70%
```

relative to the expected value.

Do not simply set throughput to one fixed abnormal number.

---

# 38. Anomaly Type 4 — Traffic / User Surge

Inject a correlated surge:

```text
Connected Users ↑
Download Traffic ↑
Upload Traffic ↑
CPU Usage ↑
```

Example relative changes:

```text
Users   +30–70%

Traffic +40–100%
```

These are synthetic scenario settings.

Latency and packet loss may rise slightly if load approaches capacity.

---

# 39. Anomaly Type 5 — CPU Overload

Push CPU to approximately:

```text
90–99%
```

for multiple intervals.

Other KPIs should not automatically fail.

This allows the model to learn a resource-specific anomaly.

---

# 40. Anomaly Type 6 — Memory Overload

Push memory usage to approximately:

```text
90–99%
```

Memory overload can persist longer than a temporary CPU spike.

---

# 41. Anomaly Type 7 — Multi-KPI Degradation

Create a correlated degradation pattern:

```text
Latency        ↑↑

Packet Loss    ↑↑

Throughput     ↓↓

CPU Usage      ↑
```

Example:

```text
Latency        × 2–4

Packet Loss    5–15%

Throughput     -40–70%

CPU            +15–30 percentage points
```

This should represent one of the stronger anomaly classes.

---

# 42. Temporary vs Persistent Events

## Temporary

Duration:

```text
1–2 intervals
```

which equals:

```text
15–30 minutes
```

---

## Persistent

Duration:

```text
4–12 intervals
```

which equals:

```text
1–3 hours
```

Persistent anomalies should later receive greater severity than equivalent
one-interval anomalies.

---

# 43. Anomaly Labels

Add:

```text
is_anomaly

anomaly_type

anomaly_id
```

Example normal row:

```text
is_anomaly  = 0
anomaly_type = "normal"
anomaly_id   = null
```

Example anomalous row:

```text
is_anomaly   = 1
anomaly_type = "packet_loss_spike"
anomaly_id   = "ANOM_0042"
```

Ground-truth labels will later be used for evaluation only.

They will not be supplied to Isolation Forest as input features.

---

# 44. Anomaly Types to Freeze for V1

Use exactly these Version 1 anomaly families:

```text
1. latency_spike

2. packet_loss_spike

3. throughput_degradation

4. traffic_surge

5. cpu_overload

6. memory_overload

7. multi_kpi_degradation
```

Temporary and persistent behavior should be implemented as:

```text
duration characteristics
```

rather than separate physical anomaly classes.

This avoids unnecessary label complexity.

---

# 45. Clean Dataset First

The first simulator should generate a technically clean dataset.

Do not intentionally add:

```text
missing values
duplicate rows
negative KPIs
broken timestamps
```

during the initial generator implementation.

Reason:

We first need to verify that the telecom behavior itself is correct.

Later, for the preprocessing stage, we can create a separate controlled
data-quality corruption step that introduces:

```text
missing values
duplicates
invalid values
```

This keeps:

```text
Network Anomalies
```

separate from:

```text
Data Quality Problems
```

which is an important engineering distinction.

---

# 46. Real-Data-Informed vs Synthetic Assumptions

## Real-data-informed

The following aspects are influenced by RANalyzer:

```text
Throughput usually follows offered load

Normal throughput efficiency is usually very high

Packet loss is strongly right-skewed

Most packet loss is near zero

Severe packet loss is rare

High-load operation can reduce efficiency

Strong throughput-degradation events are realistic

Performance degradation can involve several KPIs together
```

---

## Fully Synthetic / Engineering Assumptions

The following are not directly learned from RANalyzer:

```text
20-cell topology

Bangladesh regional labels

Cell types

Connected-user counts

Daily activity profiles

Weekend behavior

Latency baseline

CPU usage

Memory usage

Handover counts

Cell capacity values

Signal-quality baseline

Exact anomaly injection magnitudes
```

These must be documented as simulator design choices.

---

# 47. Features Not Included in V1 Synthetic Dataset

Do not include these RANalyzer features in the first simulator:

```text
BLER

MCS

NPRB

HARQ round counters

RRC event counters

Random Access counters

PDU session events

LCID counters

git_hash
```

They are useful real-network diagnostics but would add unnecessary complexity
to Version 1.

---

# 48. Final V1 Dataset Schema

The raw synthetic CSV will contain:

```text
timestamp
cell_id
region
location_type
technology

connected_users

download_traffic_gb
upload_traffic_gb

throughput_mbps
latency_ms
packet_loss_percent
signal_quality_dbm

cpu_usage_percent
memory_usage_percent
handover_count

is_anomaly
anomaly_type
anomaly_id
```

Total:

```text
18 columns
```

before later feature engineering.

---

# 49. Expected Dataset Size

```text
20 cells
×
14 days
×
96 intervals/day
=
26,880 rows
```

So the expected raw output is approximately:

```text
26,880 rows × 18 columns
```

---

# 50. Simulator Development Order

The simulator should be built in this order:

```text
1. Cell metadata
       ↓
2. Timestamp grid
       ↓
3. Daily user profiles
       ↓
4. Connected users
       ↓
5. Traffic demand
       ↓
6. Load ratio
       ↓
7. Normal throughput
       ↓
8. Normal latency
       ↓
9. Normal packet loss
       ↓
10. Signal quality
       ↓
11. CPU / memory
       ↓
12. Handover count
       ↓
13. Validate NORMAL data
       ↓
14. Inject anomalies
       ↓
15. Add ground-truth labels
```

Do not inject anomalies until normal behavior has been validated visually.

---

# 51. One Remaining Kaggle Output

The final simulator-percentile cell from Step 8 was not executed in the
uploaded notebook.

Before closing the real-data notebook, run:

```python
simulator_reference = df[
    [
        "target_rate_mbps",
        "avg_throughput_mbps",
        "avg_jitter_ms",
        "avg_packet_loss_percent",
        "avg_rsrp",
        "avg_snr",
        "avg_dl_bler",
        "avg_ul_bler",
    ]
].quantile(
    [
        0.01,
        0.05,
        0.25,
        0.50,
        0.75,
        0.95,
        0.99,
    ]
).T

simulator_reference.round(3)
```

Save the notebook version after running it.

This table is useful documentation, but it does not block the core simulator
design above.

---

# 52. Step 9 Completion Checklist

Step 9 is complete when:

- [x] Real-data findings are summarized
- [x] Real-data-informed assumptions are separated from synthetic assumptions
- [x] Network size is frozen
- [x] Time interval is frozen
- [x] Regional structure is frozen
- [x] Cell types are frozen
- [x] Raw schema is frozen
- [x] KPI units are frozen
- [x] Normal KPI relationships are documented
- [x] Packet-loss behavior is defined
- [x] Throughput behavior is defined
- [x] Latency assumptions are explicitly synthetic
- [x] Signal-quality limitations are documented
- [x] CPU and memory assumptions are documented
- [x] Handover assumptions are documented
- [x] Anomaly families are frozen
- [x] Temporary/persistent durations are defined
- [x] Anomaly prevalence target is defined
- [x] Ground-truth label fields are defined
- [x] Data-quality corruption is postponed until after normal simulator validation

---

# 53. Next Step

The next step is:

# Step 10 — Build the Normal Telecom Simulator

The first coding target should be:

```text
simulator/
├── config.py
└── generator.py
```

But Step 10 should begin with **normal data only**:

```text
20 cells
+
14 days
+
15-minute intervals
+
daily patterns
+
correlated normal KPIs
```

No anomaly injection yet.

The normal generator must first be validated before `anomaly_injector.py` is
created.
