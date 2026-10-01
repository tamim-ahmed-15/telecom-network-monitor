# Step 4 — Telecom Network Concepts and KPI Fundamentals

## Telecom Network Monitoring & Anomaly Detection System

This document contains the telecom concepts required to understand and build Version 1 of the **Telecom Network Monitoring & Anomaly Detection System**.

The goal is **not** to study complete 4G/5G theory. The goal is to understand the network entities, KPIs, relationships, and abnormal behaviors that will later appear in:

- the public 5G dataset,
- our synthetic telecom simulator,
- the anomaly-detection model,
- the FastAPI backend,
- and the React NOC dashboard.

---

# 1. Learning Objective

After completing this step, I should be able to explain:

- What a cellular network cell is
- What a base station is
- What a UE is
- What a KPI is
- What network traffic means
- Difference between bandwidth and throughput
- What latency means
- What packet loss means
- What jitter means
- What RSRP, RSRQ, SNR and SINR represent
- What CPU and memory utilization represent
- What handover means
- What network congestion means
- How network KPIs can influence each other
- How abnormal KPI behavior can be used for anomaly detection

---

# 2. Simplified Cellular Network Architecture

For this project, think about a cellular network using the following simplified flow:

```text
User Device / UE
      │
      │ Radio Link
      ▼
Cell / Base Station
(eNodeB in LTE or gNodeB in 5G)
      │
      ▼
Mobile Core Network
      │
      ▼
Internet / Application Server
```

A user sends and receives data through a nearby cellular base station.

The base station handles the radio connection between the user's device and the mobile network.

The core network handles functions such as connectivity, routing, mobility, authentication, and access to external networks.

Our project does **not** simulate all of these internal telecom procedures.

Instead, it observes performance indicators produced by the network.

---

# 3. UE — User Equipment

**UE** stands for **User Equipment**.

A UE is a device connected to the mobile network.

Examples:

- Smartphone
- 4G/5G modem
- Tablet
- IoT device
- Mobile router

Example:

```text
Smartphone
    ↓
connects to
    ↓
Cell CTG_005
```

In our project, the individual devices themselves will not be simulated in detail.

Instead, we will use:

```text
connected_users
```

to represent approximately how many users/devices are currently served by a simulated cell.

---

# 4. Base Station

A **base station** provides radio connectivity between mobile devices and the cellular network.

Common terminology:

```text
4G LTE → eNodeB / eNB
5G NR  → gNodeB / gNB
```

A physical base-station site may support one or more cells.

For our simplified software project, we do not need to model all of the differences between:

```text
Site
Sector
Radio Unit
Base Station
Cell
```

We will mainly work with a logical **cell**.

---

# 5. Cell

A **cell** is a radio coverage/service area associated with cellular-network resources.

For our project, each simulated cell will be represented by an ID such as:

```text
CTG_001
CTG_002
CTG_003
...
```

Each cell can have different characteristics.

Example:

```text
CTG_001
Location Type: Residential
Peak Load: Evening

CTG_002
Location Type: Business
Peak Load: Office Hours

CTG_003
Location Type: University
Peak Load: Daytime
```

This is important because not every cell should have the same normal behavior.

---

# 6. What Is a KPI?

**KPI** stands for **Key Performance Indicator**.

A KPI is a measurable value used to understand the condition or performance of the network.

Examples:

```text
Throughput
Latency
Packet Loss
Connected Users
Traffic Volume
Signal Quality
CPU Usage
```

A NOC engineer usually does not manually inspect every packet.

Instead, monitoring systems summarize network behavior using KPIs.

Our anomaly-detection system will therefore operate mainly on KPI measurements.

---

# 7. Timestamp

Every KPI observation needs a time.

Example:

```text
timestamp = 2026-10-01 20:30:00
```

Why is time important?

Because telecom behavior changes throughout the day.

Example:

```text
02:00 → Low traffic

09:00 → Increasing traffic

14:00 → Moderate/high traffic

21:00 → High residential traffic
```

A KPI value may be normal at one time and unusual at another.

Therefore our project will use **time-series data**.

---

# 8. Connected Users

`connected_users` represents the number of users/devices associated with or actively represented by a cell in our simplified simulator.

Example:

```text
CTG_001

02:00 → 80 users
12:00 → 310 users
20:00 → 480 users
```

More connected users often create more demand for network resources.

A simplified relationship is:

```text
Connected Users ↑
        ↓
Traffic Demand ↑
        ↓
Network Load ↑
```

However:

> More users do not automatically mean poor performance.

A properly provisioned cell may serve many users without congestion.

---

# 9. Network Traffic

Network traffic represents the amount of data being transferred through the network.

For our project:

```text
download_traffic
upload_traffic
```

will represent traffic volumes.

## Download Traffic

Data moving:

```text
Network
   ↓
User
```

Examples:

- Video streaming
- Downloading files
- Browsing websites
- Receiving social-media content

## Upload Traffic

Data moving:

```text
User
   ↓
Network
```

Examples:

- Uploading photos
- Sending files
- Video-call uplink
- Cloud backup

Typical consumer networks often carry more downlink than uplink traffic, but this depends on the application and environment.

---

# 10. Traffic Volume vs Throughput

These terms are related but are **not the same thing**.

## Traffic Volume

Traffic volume means:

> How much data was transferred.

Possible units:

```text
MB
GB
Bytes
```

Example:

```text
2 GB downloaded during 15 minutes
```

## Throughput

Throughput means:

> How fast useful data is transferred over time.

Common units:

```text
Mbps
Gbps
bits per second
```

Example:

```text
Throughput = 85 Mbps
```

So:

```text
Traffic Volume → amount of data

Throughput     → rate of data transfer
```

---

# 11. Bandwidth vs Throughput

This distinction is important.

## Bandwidth

Bandwidth usually describes the available or configured capacity of a communication channel.

## Throughput

Throughput describes the actual achieved data-transfer rate.

Conceptually:

```text
Available Capacity
      ↓
   Bandwidth
      ↓
Real Network Conditions
      ↓
Actual Achieved Rate
      ↓
   Throughput
```

Throughput may be lower because of:

- congestion,
- poor radio conditions,
- interference,
- protocol overhead,
- retransmissions,
- application limitations,
- resource limitations.

Therefore:

```text
Bandwidth ≠ Throughput
```

---

# 12. Throughput

Throughput is one of the main performance KPIs in our project.

Example:

```text
Normal:

Throughput = 90 Mbps

During degradation:

Throughput = 35 Mbps
```

A reduction in throughput may be meaningful when it occurs together with other changes.

Example:

```text
Users ↑
Traffic ↑
CPU ↑
Latency ↑
Packet Loss ↑
Throughput ↓
```

This combination may indicate degraded network performance.

But the system should describe the observed pattern rather than automatically assigning a physical root cause.

---

# 13. Latency

**Latency** is the delay involved in moving data through a network.

It is commonly measured in:

```text
milliseconds (ms)
```

Example:

```text
Latency = 35 ms
```

means the measured communication experienced approximately 35 milliseconds of delay according to the measurement method being used.

Two common concepts are:

## One-Way Delay

```text
Sender → Receiver
```

## Round-Trip Time — RTT

```text
Sender
   ↓
Receiver
   ↓
Sender
```

RTT measures the time for a request/message to travel to the destination and for a response to return.

When analyzing a dataset, we must check whether its latency column represents:

```text
One-way latency
or
Round-trip latency
```

We should never assume this without checking the dataset documentation.

---

# 14. Why Latency Increases

Latency can increase because of many factors such as:

- Network congestion
- Queueing
- Longer network path
- Processing delay
- Retransmissions
- Server/application delay
- Radio conditions

For anomaly detection:

```text
Current Latency
       ↓
Compare with
       ↓
Cell Historical Baseline
```

Example:

```text
Normal baseline = 35 ms

Current = 160 ms
```

The current value is clearly unusual relative to that cell's own recent behavior.

---

# 15. Packet Loss

Networks transfer information using packets.

**Packet loss** occurs when some transmitted packets do not successfully reach their expected destination.

Usually expressed as:

```text
Percentage (%)
```

Example:

```text
1000 packets transmitted
10 packets lost

Packet loss = 1%
```

Formula:

```text
Packet Loss (%) =
Lost Packets / Total Sent Packets × 100
```

High packet loss can negatively affect:

- Voice calls
- Video calls
- Gaming
- Streaming
- Downloads
- Interactive applications

In our monitoring system, a sudden increase in packet loss can be an important anomaly indicator.

---

# 16. Jitter

**Jitter** is the variation in packet delay.

Suppose packets are expected to arrive regularly.

Example:

```text
Packet 1 → delay 30 ms
Packet 2 → delay 31 ms
Packet 3 → delay 29 ms
Packet 4 → delay 70 ms
```

The delay is not stable.

This variation is jitter.

Jitter is particularly important for real-time applications such as:

- Voice
- Video conferencing
- Live streaming
- Online gaming

RANalyzer contains `jitter_ms`, so we should understand this KPI even though it is not currently one of the core dashboard KPIs.

---

# 17. Relationship Between Latency, Jitter, and Packet Loss

These are different measurements.

```text
Latency
= How long packets take

Jitter
= How much packet delay varies

Packet Loss
= How many packets never arrive successfully
```

Example:

```text
Latency     = 40 ms
Jitter      = 3 ms
Packet Loss = 0.2%
```

A degraded network may show:

```text
Latency     ↑
Jitter      ↑
Packet Loss ↑
```

But they do not always increase together.

---

# 18. Signal Quality

Wireless communication depends on the quality of the radio link between:

```text
UE
 ↕
Base Station
```

Radio datasets may contain measurements such as:

```text
RSRP
RSRQ
SNR
SINR
```

These values help describe radio conditions.

---

# 19. RSRP

**RSRP** stands for:

**Reference Signal Received Power**

It represents the received power level of specific reference signals used by the cellular system.

It is commonly expressed in:

```text
dBm
```

Example:

```text
RSRP = -80 dBm
```

or:

```text
RSRP = -110 dBm
```

Because these numbers are negative:

```text
-80 dBm
```

is stronger than:

```text
-110 dBm
```

So conceptually:

```text
Less negative RSRP
       ↓
Stronger received reference signal
```

However, RSRP alone does not tell us everything about network quality.

A strong signal can still experience poor performance because of:

- interference,
- congestion,
- resource limitations,
- poor signal quality,
- retransmissions.

---

# 20. RSRQ

**RSRQ** stands for:

**Reference Signal Received Quality**

While RSRP focuses mainly on reference-signal power, RSRQ gives information about the quality of the received radio environment relative to total received power.

RSRQ is useful because a user may have:

```text
Strong received signal
```

but still experience:

```text
Interference
or
high network load
```

and therefore poorer overall radio quality.

RSRQ is commonly represented in dB.

As a general interpretation, less-negative/higher RSRQ values usually represent better radio quality, but exact thresholds depend on system configuration and measurement definitions.

For this project, we should avoid hard-coding universal RSRQ quality thresholds unless supported by the dataset or an explicit engineering assumption.

---

# 21. SNR

**SNR** stands for:

**Signal-to-Noise Ratio**

Conceptually:

```text
Desired Signal Power
--------------------
Noise Power
```

It tells us how strong the desired signal is compared with background noise.

Common unit:

```text
dB
```

Higher SNR generally means a cleaner signal.

Conceptually:

```text
Signal >> Noise
     ↓
Higher SNR
     ↓
Usually better radio conditions
```

---

# 22. SINR

**SINR** stands for:

**Signal-to-Interference-plus-Noise Ratio**

Conceptually:

```text
Desired Signal
-------------------------
Interference + Noise
```

This is especially useful in cellular networks because interference from other transmissions can affect radio performance.

In general:

```text
Higher SINR
    ↓
Better radio conditions
    ↓
Potentially higher usable modulation/coding
    ↓
Potentially better throughput
```

Again, this is a relationship, not a guaranteed rule.

---

# 23. SNR vs SINR

The difference is:

```text
SNR
= Signal compared with Noise

SINR
= Signal compared with Noise + Interference
```

Because cellular systems can experience interference, SINR often gives a more complete picture of radio quality.

---

# 24. Signal Quality in Our Version 1 Dataset

Our simplified application schema contains:

```text
signal_quality
```

Initially we may represent this using a simplified radio-quality measurement, most likely based on a real dataset field such as:

```text
RSRP
```

or another clearly documented radio KPI.

We should not combine different metrics into an undefined value without documenting exactly how it was calculated.

---

# 25. CPU Utilization

Modern telecom network functions depend heavily on computing resources.

**CPU utilization** describes how much processor capacity is being used.

Usually:

```text
0% to 100%
```

Example:

```text
CPU Usage = 42%
```

High load example:

```text
CPU Usage = 94%
```

A simplified relationship in our simulator may be:

```text
Traffic ↑
    ↓
Processing Demand ↑
    ↓
CPU Usage ↑
```

However:

> High CPU does not automatically mean network failure.

It becomes more interesting when combined with other abnormal behavior.

Example:

```text
CPU ↑
Latency ↑
Packet Loss ↑
Throughput ↓
```

---

# 26. Memory Utilization

**Memory utilization** represents how much available system memory is currently being used.

Example:

```text
Memory Usage = 65%
```

Our synthetic simulator will include memory usage because it is useful for demonstrating infrastructure monitoring.

However, we must clearly state that memory utilization is a simulated NOC feature if it is not available in our real reference dataset.

---

# 27. Handover

A mobile user may move from the coverage area of one cell toward another.

The network can transfer the active connection from one serving cell to another.

This process is called a **handover**.

Simplified example:

```text
UE connected to Cell A
        ↓
User moves
        ↓
Signal from Cell B becomes preferable
        ↓
Connection transferred
        ↓
UE connected to Cell B
```

Handover supports mobility.

Examples:

- User travelling in a car
- User walking between coverage areas
- Train passenger moving through several cells

---

# 28. Handover Count

Our project may contain:

```text
handover_count
```

for each monitoring interval.

Example:

```text
15-minute period:

handover_count = 42
```

The expected handover count may depend on location type.

Example:

```text
Residential Cell
→ relatively stable population

Transport Cell
→ potentially more mobility
→ potentially more handovers
```

A sudden unusual handover pattern may be useful as a contextual anomaly feature.

But we should not assume that every high handover count is a problem.

---

# 29. Network Congestion

Network congestion occurs when network demand approaches or exceeds available resources/capacity in some part of the system.

Simple analogy:

```text
Road

Few cars
→ Traffic flows easily

Too many cars
→ Congestion
→ Travel time increases
```

Telecom analogy:

```text
Network Demand ↑
        ↓
Available Resources Become Busy
        ↓
Queueing / Scheduling Pressure ↑
        ↓
Possible Performance Degradation
```

Possible observable patterns:

```text
Latency ↑
Packet Loss ↑
Throughput/user ↓
CPU/Resource Usage ↑
```

However, our anomaly detector should say:

```text
"Observed behavior is consistent with performance degradation."
```

rather than:

```text
"Congestion definitely caused the problem."
```

unless we have enough evidence to support that diagnosis.

---

# 30. Network Load

**Network load** is a general concept describing how heavily network resources are being used.

Load may be influenced by:

```text
Connected users
Traffic demand
Radio resource usage
Processing demand
Number of active sessions
```

There is no single universal "network load" column.

Different systems use different indicators.

In our simulator, network load will be represented indirectly through several correlated KPIs.

---

# 31. PRB — Physical Resource Block

This is an additional term that may appear in real LTE/5G datasets.

**PRB** means **Physical Resource Block**.

PRBs are radio resources allocated for transmitting user data.

A simplified interpretation:

```text
More Traffic Demand
       ↓
More Radio Resources Needed
       ↓
PRB Utilization ↑
```

High PRB utilization can indicate that radio resources are heavily used.

We do not need PRB utilization in the first application schema, but it may be useful when studying real datasets.

---

# 32. MCS — Modulation and Coding Scheme

**MCS** stands for:

**Modulation and Coding Scheme**

The network selects different modulation/coding configurations depending on radio conditions and other scheduling factors.

Conceptually:

```text
Better radio conditions
       ↓
Potentially more efficient MCS
       ↓
More information transmitted
per radio resource
```

Poor radio conditions may require more robust settings.

MCS is an important radio-level metric, but Version 1 does not need to display MCS on the main dashboard.

We only need to understand it when examining real 5G logs.

---

# 33. BLER — Block Error Rate

**BLER** stands for:

**Block Error Rate**

It represents the proportion of transmitted data blocks that are received incorrectly and require handling such as retransmission.

Conceptually:

```text
High BLER
   ↓
More transmission errors
   ↓
Possible retransmissions
   ↓
Potential performance degradation
```

BLER is useful when analyzing radio-link reliability.

The RANalyzer gNB logs include BLER-related measurements, so knowing this term will help us later.

---

# 34. HARQ

**HARQ** stands for:

**Hybrid Automatic Repeat Request**

It is a retransmission mechanism used when transmitted radio data is not decoded successfully.

Simplified:

```text
Base Station Sends Data
        ↓
UE tries to decode
        ↓
Failure
        ↓
Retransmission requested/performed
        ↓
Receiver combines information
```

More HARQ retransmissions may indicate difficulty delivering data successfully.

But retransmissions are normal parts of wireless communication; they are not automatically anomalies.

---

# 35. RRC

**RRC** stands for:

**Radio Resource Control**

RRC handles important control procedures between the UE and radio network.

Examples include:

- Connection establishment
- Measurement configuration
- Mobility-related control
- Radio resource configuration

RANalyzer contains gNB logs with RRC-related events.

We do not need to implement RRC behavior in Version 1.

---

# 36. Traffic Rate / Target Rate in RANalyzer

RANalyzer uses controlled traffic tests.

A field such as:

```text
target_rate_mbps
```

represents the data rate the test attempts to send.

The measured:

```text
bits_per_second
```

or throughput represents the actually observed transfer rate.

Conceptually:

```text
Target Rate
     ↓
Traffic Generator Attempts
     ↓
Network Carries Traffic
     ↓
Measured Throughput
```

These values are not necessarily identical.

This distinction will be important during real-dataset analysis.

---

# 37. Bytes Transferred

Real network datasets may provide:

```text
bytes
```

This tells us how much data was transferred during an interval.

Example:

```text
bytes = 10,000,000
```

This is a **volume**, not a rate.

To obtain a rate, both:

```text
Data Amount
and
Time
```

are needed.

---

# 38. Active Connections

A monitoring system may track how many active sessions/connections exist.

Our Version 1 currently uses:

```text
connected_users
```

rather than separately modeling every network connection.

Later versions could distinguish:

```text
Connected Users
Active Sessions
Active Data Flows
```

but this is unnecessary for the first implementation.

---

# 39. KPI Relationships — The Most Important Concept

Our ML model should not see every KPI as unrelated.

Normal network behavior may contain relationships.

Example:

```text
Connected Users ↑
        ↓
Traffic ↑
        ↓
CPU Usage ↑
```

Under heavy load:

```text
Traffic Demand ↑
        ↓
Resource Pressure ↑
        ↓
Latency may ↑
Packet Loss may ↑
Throughput/user may ↓
```

Radio effects may create another pattern:

```text
Signal Quality ↓
       ↓
Transmission Efficiency may ↓
       ↓
Retransmissions may ↑
       ↓
Throughput may ↓
```

The word **may** is important.

These are plausible relationships, not deterministic equations.

---

# 40. Correlation Does Not Mean Causation

Suppose we observe:

```text
CPU Usage ↑
Latency ↑
```

We cannot immediately claim:

```text
"High CPU caused the latency."
```

We only know they occurred together.

There may be another reason affecting both.

Our application should therefore report **observations**.

Good:

```text
CPU utilization and latency are both significantly
above their historical baselines.
```

Avoid:

```text
CPU overload caused the network failure.
```

unless we actually have evidence for that conclusion.

---

# 41. Normal Behavior Depends on Context

A fixed global threshold is often too simple.

Example:

```text
Cell A normal latency = around 25 ms

Cell B normal latency = around 55 ms
```

Current:

```text
Both cells = 60 ms
```

Interpretation:

```text
Cell A
60 ms may be unusual

Cell B
60 ms may be close to normal
```

Therefore our project will eventually compare:

```text
Current KPI
    +
Cell-specific history
    +
Time-of-day behavior
```

This is why historical baselines are important.

---

# 42. Time-of-Day Behavior

Telecom networks often exhibit time-dependent demand.

Our simplified simulator may model:

```text
00:00–06:00
Low demand

07:00–10:00
Increasing demand

10:00–17:00
Moderate demand

18:00–23:00
High residential demand
```

But different cell types will have different profiles.

Example:

```text
Residential
→ evening peak

Business
→ office-hour peak

University
→ daytime activity

Transport
→ mobility-driven variation
```

These are simulation assumptions that must be documented as assumptions, not presented as universal operator behavior.

---

# 43. Temporary vs Persistent Abnormal Behavior

Not every unusual value should become a critical alarm.

## Temporary

```text
Normal
Normal
Abnormal
Normal
Normal
```

A one-interval spike may be caused by temporary variation.

## Persistent

```text
Normal
Abnormal
Abnormal
Abnormal
Abnormal
Abnormal
```

Persistent abnormal behavior is generally more operationally important.

Therefore our future severity engine will consider:

```text
Magnitude
+
Number of KPIs affected
+
Anomaly score
+
Persistence
```

---

# 44. Main Anomaly Patterns for Version 1

## Pattern 1 — Latency Spike

```text
Latency ↑↑
Other KPIs mostly stable
```

Possible system statement:

```text
Latency is significantly above the historical baseline.
```

---

## Pattern 2 — Packet-Loss Spike

```text
Packet Loss ↑↑
```

Possible system statement:

```text
Packet loss is significantly higher than expected.
```

---

## Pattern 3 — Throughput Degradation

```text
Throughput ↓↓
```

Possible statement:

```text
Throughput is substantially below its historical baseline.
```

---

## Pattern 4 — Traffic Surge

```text
Users ↑
Traffic ↑↑
CPU ↑
```

Possible statement:

```text
Traffic and connected-user activity are substantially
above the expected level.
```

---

## Pattern 5 — Resource Overload Pattern

```text
CPU ↑↑
Memory ↑↑
```

Possible statement:

```text
Compute resource utilization is unusually high.
```

---

## Pattern 6 — Multi-KPI Degradation

```text
Latency ↑
Packet Loss ↑
Throughput ↓
CPU ↑
```

Possible statement:

```text
Multiple network-performance KPIs are outside their
historical baselines.
```

This will likely be treated as a more severe anomaly.

---

# 45. KPI Units We Must Track Carefully

| KPI | Typical Unit in Our Project | Meaning |
|---|---|---|
| `connected_users` | count | Number of users/devices |
| `download_traffic` | MB/GB per interval | Download data volume |
| `upload_traffic` | MB/GB per interval | Upload data volume |
| `throughput` | Mbps | Data-transfer rate |
| `latency` | ms | Network delay |
| `packet_loss` | % | Lost packet percentage |
| `jitter` | ms | Variation in packet delay |
| `signal_quality` | depends on selected metric | Radio quality |
| `RSRP` | dBm | Reference signal received power |
| `RSRQ` | dB | Reference signal received quality |
| `SNR/SINR` | dB | Signal quality relative to noise/interference |
| `cpu_usage` | % | Processor utilization |
| `memory_usage` | % | Memory utilization |
| `handover_count` | count | Number of handovers |
| `BLER` | ratio/% | Block transmission error level |
| `target_rate_mbps` | Mbps | Requested/configured traffic rate |

Always check dataset documentation before assuming units.

---

# 46. Direction of Common KPI Changes

This is a useful quick-reference table.

| KPI | Generally Better Direction | Important Note |
|---|---|---|
| Throughput | Higher | Depends on demand/capacity |
| Latency | Lower | Measurement method matters |
| Packet Loss | Lower | Near-zero is desirable in many services |
| Jitter | Lower | Important for real-time services |
| RSRP | Less negative / stronger | Signal power only |
| RSRQ | Higher / less negative | Exact interpretation depends on system |
| SNR/SINR | Higher | Better signal relative to noise/interference |
| CPU Usage | Neither always | High can be normal under load |
| Memory Usage | Neither always | Depends on system design |
| Users | Neither | High users are not inherently bad |
| Traffic | Neither | High traffic can be normal |
| Handovers | Neither | Depends strongly on mobility/context |
| BLER | Lower generally | Some errors/retransmissions are expected |

This table should **not** be used as a universal alarm-threshold table.

---

# 47. Why We Need Multiple KPIs

Imagine:

```text
Latency = 100 ms
```

Alone, we have limited context.

Now suppose:

```text
Latency      ↑
Packet Loss  ↑
Throughput   ↓
CPU          ↑
Traffic      ↑
```

This gives much stronger evidence that something unusual is happening.

This is why our system will use **multivariate anomaly detection**.

`multivariate` simply means:

> Looking at several variables/KPIs together.

---

# 48. What the ML Model Will Eventually Learn

The Isolation Forest will receive features representing network behavior.

Possible inputs:

```text
connected_users
download_traffic
upload_traffic
throughput
latency
packet_loss
signal_quality
cpu_usage
memory_usage
handover_count

traffic_per_user
latency_change
packet_loss_change
throughput_change

rolling_latency_mean
rolling_packet_loss_mean
rolling_throughput_mean

latency_deviation_from_baseline
packet_loss_deviation_from_baseline
throughput_deviation_from_baseline
```

The model does not directly understand words such as:

```text
congestion
bad network
failure
```

It only sees numerical patterns.

That is why our application needs a separate **explanation engine**.

---

# 49. Detection vs Diagnosis

This distinction is essential.

## Detection

```text
"This observation is unusual."
```

This is what the anomaly model does.

## Explanation

```text
"Latency and packet loss are significantly above
their historical baselines."
```

This is what our explanation engine does.

## Diagnosis / Root Cause

```text
"The antenna feeder has failed."
```

This requires much stronger evidence and is outside Version 1.

Therefore:

```text
Anomaly Detection
≠
Physical Fault Diagnosis
```

---

# 50. Severity Is Also Different From Detection

The ML model may detect an anomaly.

Then our severity engine determines its operational importance.

Example:

```text
Small one-time deviation
→ WARNING
```

while:

```text
Large deviation
+
Several KPIs affected
+
Persistent for multiple intervals
→ CRITICAL
```

So:

```text
Detection
      ↓
Is this unusual?

Severity
      ↓
How important does it appear?
```

---

# 51. Our Simplified Version 1 Network Model

We are deliberately simplifying a real mobile network.

Our main logical model will be:

```text
Cell
 │
 ├── Connected Users
 │
 ├── Download Traffic
 │
 ├── Upload Traffic
 │
 ├── Signal Quality
 │
 ├── CPU Usage
 │
 ├── Memory Usage
 │
 ├── Handover Count
 │
 └── Performance
      ├── Throughput
      ├── Latency
      └── Packet Loss
```

We are **not** attempting to simulate:

- Full 3GPP protocol stack
- Detailed radio propagation
- Scheduler implementation
- 5G core procedures
- Complete mobility-management algorithms
- Physical antenna faults
- Full packet-level network simulation

This keeps the project realistic enough for learning while still manageable.

---

# 52. How the Real Dataset Fits

The public **RANalyzer** dataset contains real end-to-end 5G performance measurements from a private 5G testbed.

Its data includes measurements such as:

```text
Throughput
Jitter
Packet loss
Bytes transferred
CPU utilization
Target traffic rate
```

and its gNB logs include radio/protocol information such as:

```text
RSRP
SNR
BLER
MCS
HARQ retransmissions
RRC events
MAC/RLC counters
```

We will use this real data to learn:

```text
What realistic measurements look like

How KPI values are distributed

Which KPIs move together

How extreme measurements look

Which features are useful for our simulator
```

We will **not** pretend that the final simulated 20-cell NOC dataset is actual operator data.

---

# 53. Real Dataset vs Our Dataset

Example mapping:

| Real Dataset Concept | Our NOC Feature |
|---|---|
| Throughput / bits per second | `throughput` |
| Packet-loss percentage | `packet_loss` |
| CPU utilization | `cpu_usage` |
| RSRP or similar radio metric | `signal_quality` |
| Bytes transferred | Reference for traffic behavior |
| Jitter | Optional analysis feature |
| SNR | Real-data radio analysis |
| BLER/MCS/HARQ | Extra radio-level understanding |

Features such as:

```text
connected_users
memory_usage
handover_count
cell location type
```

may need to be simulated if they are not available in the chosen real dataset.

---

# 54. Important Dataset Rule

Never assume that two columns from different datasets mean exactly the same thing simply because their names sound similar.

For each dataset column we must determine:

```text
Name
Meaning
Unit
Measurement Method
Aggregation Interval
Source
```

Example:

```text
latency
```

could mean:

```text
One-way latency
RTT
Application latency
Radio latency
End-to-end network latency
```

Those are not automatically interchangeable.

This is why the next dataset-analysis stage will start with a **data dictionary**.

---

# 55. NOC — Network Operations Center

A **Network Operations Center (NOC)** is an operational environment where engineers monitor network health and respond to problems.

A simplified NOC dashboard might show:

```text
Total Cells
Healthy Cells
Warning Cells
Critical Cells

Average Latency
Average Throughput
Packet Loss

Active Alarms

Historical KPI Charts
```

Our React application will imitate this monitoring style.

It is not intended to reproduce a commercial operator NOC platform exactly.

---

# 56. Example End-to-End Monitoring Scenario

Normal behavior:

```text
Cell: CTG_102

Users          = 410
Throughput     = 88 Mbps
Latency        = 36 ms
Packet Loss    = 0.5%
CPU            = 54%
```

Later:

```text
Users          = 430
Throughput     = 41 Mbps
Latency        = 175 ms
Packet Loss    = 8.1%
CPU            = 84%
```

Our application may determine:

```text
Anomaly = True
```

Then explanation:

```text
Latency is significantly above the cell's historical baseline.

Packet loss is significantly above its historical baseline.

Throughput is substantially below the expected range.
```

Severity may become:

```text
HIGH
```

Notice what we did **not** say:

```text
Antenna is broken.
```

We only report observations supported by data.

---

# 57. Key Relationships to Remember

## Relationship A

```text
Users ↑
   ↓
Traffic Demand ↑
```

## Relationship B

```text
Traffic ↑
   ↓
Processing Demand ↑
   ↓
CPU may ↑
```

## Relationship C

```text
Heavy Load
   ↓
Queueing may ↑
   ↓
Latency may ↑
```

## Relationship D

```text
Poor Radio Conditions
   ↓
Transmission Efficiency may ↓
   ↓
Retransmissions may ↑
   ↓
Throughput may ↓
```

## Relationship E

```text
Severe Network Stress
   ↓
Packet Loss may ↑
```

All should be interpreted as **possible relationships**, not guaranteed causation.

---

# 58. Terms I Should Be Able to Explain in an Interview

## Cell

A logical cellular coverage/service area through which users access the radio network.

## UE

A user device connected to the cellular network.

## KPI

A measurable indicator used to monitor network performance or condition.

## Traffic

The amount of data being transferred.

## Throughput

The achieved data-transfer rate.

## Latency

The time delay experienced by communication across the measured path.

## Packet Loss

The percentage or count of transmitted packets that fail to arrive successfully.

## Jitter

Variation in packet delay.

## RSRP

Received power of cellular reference signals.

## RSRQ

A reference-signal quality measurement that incorporates received signal and total received power.

## SNR

Ratio between desired signal power and noise.

## SINR

Ratio between desired signal power and interference-plus-noise.

## Handover

Transfer of an active mobile connection from one serving cell to another.

## Congestion

A condition where network demand places heavy pressure on available resources/capacity and may degrade performance.

## Anomaly

An observation or pattern that differs substantially from expected behavior.

---

# 59. What We Need for Version 1

## Core KPIs

We will actively use:

```text
connected_users
download_traffic
upload_traffic
throughput
latency
packet_loss
signal_quality
cpu_usage
memory_usage
handover_count
```

## Supporting Concepts

We should understand:

```text
jitter
RSRP
RSRQ
SNR
SINR
PRB
MCS
BLER
HARQ
RRC
```

but they do not all need to appear on the final dashboard.

---

# 60. What We Do NOT Need to Master Yet

Do not delay the project trying to master:

- Complete LTE architecture
- Complete 5G architecture
- OFDM mathematics
- MIMO mathematics
- Detailed channel coding
- Full 3GPP protocol specifications
- RRC state-machine details
- Scheduling algorithms
- 5G core signaling
- Detailed radio propagation models

We can learn these later if the project specifically requires them.

For Version 1, understanding the KPIs and their relationships is enough.

---

# 61. Step 4 Completion Checklist

Before moving to the real dataset, I should be comfortable answering:

- [ ] What is a cell?
- [ ] What is a base station?
- [ ] What is a UE?
- [ ] What is a KPI?
- [ ] What is network traffic?
- [ ] What is the difference between traffic volume and throughput?
- [ ] What is the difference between bandwidth and throughput?
- [ ] What is latency?
- [ ] What is RTT?
- [ ] What is packet loss?
- [ ] What is jitter?
- [ ] What is RSRP?
- [ ] What is RSRQ?
- [ ] What is SNR?
- [ ] What is SINR?
- [ ] What does CPU utilization tell us?
- [ ] What is handover?
- [ ] What is congestion?
- [ ] Why can normal behavior differ between cells?
- [ ] Why do historical baselines matter?
- [ ] Why should several KPIs be analyzed together?
- [ ] Why does correlation not prove causation?
- [ ] What is the difference between anomaly detection and root-cause diagnosis?
- [ ] Why are temporary and persistent anomalies different?

If I can explain these concepts in simple words, Step 4 is complete.

---

# 62. Next Step

After this concept stage, the next task is to obtain and inspect the first real public 5G dataset.

The workflow will become:

```text
Telecom Concepts
       ↓
Real 5G Dataset
       ↓
Data Dictionary
       ↓
Kaggle Inspection
       ↓
EDA
       ↓
Learn Real KPI Behavior
```

The next stage should start by downloading the **RANalyzer processed dataset**, identifying every useful column, and creating a proper mapping between the real dataset and our Version 1 NOC schema.

---

# References

The following sources were used to verify terminology relevant to this project:

1. RANalyzer Dataset — real end-to-end 5G measurements, including iPerf3 throughput, jitter, packet loss, CPU utilization and gNB radio/protocol logs:
   - https://github.com/wineslab/RANalyzer-Dataset

2. ETSI / 3GPP TS 38.215 — NR physical-layer measurement definitions, including reference-signal quality concepts:
   - https://www.etsi.org/deliver/etsi_ts/138200_138299/138215/

3. ETSI / 3GPP TS 38.331 — NR Radio Resource Control specification and RSRP/RSRQ/SINR measurement/reporting quantities:
   - https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/

4. Cisco documentation on network delay, jitter and packet loss:
   - https://www.cisco.com/c/en/us/support/docs/availability/high-availability/24121-saa.html

---

## Final Reminder

For this project, the most important mental model is:

```text
Network Activity
       ↓
KPIs
       ↓
Historical Context
       ↓
Abnormal Pattern Detection
       ↓
Explanation
       ↓
Monitoring Dashboard
```

We are building a system that **observes and detects unusual network behavior**.

We are not building a system that automatically proves the physical root cause of every telecom fault.
