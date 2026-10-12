# RANalyzer Processed Dataset — Final Data Dictionary

## Step 6 Status

**Completed.**

This document finalizes the data dictionary for the local RANalyzer
`processed-dataset.csv` used as the first real 5G reference source in the
**Telecom Network Monitoring & Anomaly Detection System**.

The profile contains **84 columns**. The local file contains **8,611 unique
`log_id` values**, with `log_id` showing no missing values in the generated
profile. The unit of observation is one aggregated 5G test run.

> Important: the public repository reports more raw test runs than appear in
> this processed table. For this project, the processed CSV actually profiled
> on the local machine is the source of truth for downstream analysis.

---

## 1. What RANalyzer Represents

RANalyzer was collected on a controlled private 5G testbed using
OpenAirInterface (OAI) gNB software. Each end-to-end test sends **downlink
UDP traffic** with iPerf3 at a configured target bitrate. The processed file
combines application/end-to-end KPIs with features extracted from OAI gNB
logs.

The real dataset is being used to understand realistic network-performance
measurements and relationships. It is **not** commercial operator NOC data.

---

## 2. Main Findings From the Profile

### Directly useful for our Version 1 simulator

The strongest real reference features are:

- `target_rate_mbps`
- `avg_throughput_mbps`
- `avg_packet_loss_percent`
- `total_bytes`
- `avg_rsrp`
- `avg_snr`
- `mac_tx`
- `mac_rx`

`avg_jitter_ms` is also useful as an optional network-quality KPI.

### Useful radio diagnostics, but not required in the V1 application

These include:

- BLER
- MCS
- NPRB
- DLSCH/ULSCH errors
- DTX counters
- HARQ round counters

They are useful for understanding why performance can vary, but they do not
need to become primary dashboard fields.

### Protocol-event features outside the V1 scope

Random Access, RRC, PDU-session, NGAP and UE-removal counters are valid
features extracted from gNB logs, but they are not necessary for our
beginner-friendly NOC Version 1.

### Important missing V1 NOC fields

The profiled processed CSV does **not** provide a direct suitable field for:

- `latency`
- `connected_users`
- `memory_usage`
- `region`
- `location_type`
- application-level `upload_traffic`

It also does not contain a clearly documented processed CPU-utilization
column even though the raw iPerf3 artifacts described by the source include
CPU utilization.

Therefore these fields must not be falsely described as coming from this
processed CSV.

### Handover requires caution

`ho_log` appears handover-related from its name, but its exact extraction
semantics are not documented sufficiently in the public dataset description.
It remains **REVIEW** and will not be used directly as our simulator's
`handover_count` unless verified later.

---

## 3. Missingness Findings

Several fields deserve special treatment:

- `avg_snr`, `min_snr`, `max_snr`, and `avg_nprb` have **22.94% missingness**.
- the `*_mcs0` fields have **74.75% missingness**.
- the corresponding `*_mcs1` fields have no missing values in this profile.
- `mac_ul_discard_events`, `active_pdu_session`, `protocol_stack`, and
  `flow_type` have no useful variation in the profiled file.

High missingness does not automatically make a field invalid, but it is a
good reason not to make those fields central to our Version 1 model.

---

## 4. Final Column Dictionary

| Column | dtype | Missing % | Unique | Example values | Meaning | Unit | Source / layer | NOC mapping | Decision |
|---|---|---:|---:|---|---|---|---|---|---|
| `log_id` | `str` | 0.00% | 8611 | 20231118_002818 / 20231118_002838 / 20231118_002857 | Unique timestamp-based test-run identifier in `YYYYMMDD_HHMMSS` form. | None | Dataset assembly metadata | `timestamp` can be parsed from this; do not use as numeric ML feature. | **KEEP — metadata** |
| `protocol_stack` | `str` | 0.00% | 1 | OAI | RAN software stack used for the test; all profiled rows are OAI. | None | Test metadata | Technology/context metadata only. | **KEEP — metadata** |
| `git_hash` | `str` | 0.00% | 65 | 0accb60 / ee287d6 / c5aeaf0 | Git commit/revision identifier of the OAI software tested. | None | CI/CD software metadata | No direct V1 NOC KPI mapping; useful for grouping software releases. | **KEEP — metadata** |
| `flow_type` | `str` | 0.00% | 1 | udp | Traffic transport/type used by iPerf3; current profiled data is UDP. | None | iPerf3 metadata | Traffic-test context only; constant in current data. | **KEEP — metadata** |
| `target_rate_mbps` | `float64` | 0.00% | 14 | 10.0 / 20.0 / 30.0 | Configured/requested downlink UDP traffic rate for the test. | Mbps | iPerf3 | Reference for offered traffic/load; helps calibrate load vs performance. | **KEEP — reference KPI** |
| `avg_throughput_mbps` | `float64` | 0.00% | 1216 | 9.98 / 19.95 / 29.83 | Average measured throughput over the test run. | Mbps | iPerf3 | Direct reference for future `throughput`. | **KEEP — reference KPI** |
| `avg_jitter_ms` | `float64` | 0.00% | 4360 | 0.2215 / 0.1038 / 0.0288 | Average variation in packet delay over the UDP test. | ms | iPerf3 | Optional quality KPI; not a required V1 NOC field. | **KEEP — optional** |
| `avg_packet_loss_percent` | `float64` | 0.00% | 471 | 0.18 / 0.26 / 0.37 | Average percentage of UDP packets lost during the test. | % | iPerf3 | Direct reference for future `packet_loss`. | **KEEP — reference KPI** |
| `throughput_efficiency_percent` | `float64` | 0.00% | 992 | 99.83 / 99.74 / 99.42 | Measured throughput relative to configured target rate; paper defines efficiency from actual/target throughput. | % | Derived from iPerf3 KPIs | Useful performance indicator, but not a direct NOC schema field. | **DERIVED** |
| `total_packets` | `float64` | 0.00% | 2399 | 8942.0 / 17884.0 / 26769.0 | Total UDP packets counted over the test. | packets | iPerf3 | Traffic-volume/reliability context. | **KEEP — optional** |
| `total_lost_packets` | `float64` | 0.00% | 1056 | 16.0 / 47.0 / 100.0 | Total UDP packets reported lost over the test. | packets | iPerf3 | Supports packet-loss/reliability analysis. | **KEEP — optional** |
| `total_bytes` | `float64` | 0.00% | 3051 | 12478548.0 / 24936126.0 / 37283262.0 | Total application traffic bytes transferred during the downlink iPerf3 test. | bytes | iPerf3 | Reference for `download_traffic`; not an upload-traffic measurement. | **KEEP — reference KPI** |
| `test_duration_seconds` | `float64` | 0.00% | 12 | 10.0 / 20.0 / 30.0 | Duration of the iPerf3 test run. | seconds | iPerf3 metadata | Used for normalization/quality checks; not a NOC KPI. | **KEEP — metadata** |
| `num_intervals` | `float64` | 0.00% | 12 | 10.0 / 20.0 / 30.0 | Number of iPerf3 reporting intervals aggregated for the test. | count | iPerf3 metadata | Quality/aggregation metadata only. | **KEEP — metadata** |
| `msg1_found` | `float64` | 0.00% | 455 | 2.0 / 3.0 / 5.0 | Count of logged Random Access Msg1/preamble detections. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `gnb_preparing_msg2` | `float64` | 0.00% | 410 | 2.0 / 3.0 / 4.0 | Count of logged events where the gNB prepares Random Access Msg2. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `msg2_sent` | `float64` | 0.00% | 185 | 0.0 / 2.0 / 3.0 | Count of logged Random Access Msg2 transmissions. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `msg2_cce_failure` | `float64` | 0.00% | 69 | 0.0 / 2.0 / 16.0 | Count of logged Msg2 control-channel/CCE allocation failure events. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `failed_msg2_ra_window` | `float64` | 0.00% | 121 | 0.0 / 6.0 / 23.0 | Count of logged Msg2 failures associated with the Random Access response window. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `msg3_scheduled` | `float64` | 0.00% | 370 | 0.0 / 2.0 / 133.0 | Count of logged Random Access Msg3 scheduling events. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `msg3_retransmission` | `float64` | 0.00% | 419 | 0.0 / 5.0 / 6.0 | Count of logged Msg3 retransmission events. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `msg3_cce_failure_ULgrant` | `float64` | 0.00% | 112 | 0.0 / 14.0 / 26.0 | Count of logged Msg3 uplink-grant CCE failure events. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `msg3_received` | `float64` | 0.00% | 300 | 2.0 / 86.0 / 162.0 | Count of logged Msg3 reception events. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `failed_msg3` | `float64` | 0.00% | 104 | 0.0 / 10.0 / 6.0 | Count of logged Msg3 failure events. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `successful_msg3_decoding` | `float64` | 0.00% | 47 | 0.0 / 4.0 / 2.0 | Count of logged successful Msg3 decoding events. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `gnb_preparing_msg4` | `float64` | 0.00% | 24 | 0.0 / 2.0 / 3.0 | Count of logged events where the gNB prepares Random Access Msg4. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `successful_cbra` | `float64` | 0.00% | 44 | 0.0 / 4.0 / 2.0 | Count of logged successful contention-based random-access completions. | event count | gNB log — Random Access | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `rrc_setup` | `float64` | 0.00% | 33 | 0.0 / 2.0 / 4.0 | Count of logged RRC setup events. | event count | gNB log — RRC/PDU control | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `rrc_security_setup` | `float64` | 0.00% | 11 | 0.0 / 2.0 / 4.0 | Count of logged RRC security-setup events. | event count | gNB log — RRC/PDU control | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `ue_capability_exchange` | `float64` | 0.00% | 11 | 0.0 / 2.0 / 4.0 | Count of logged UE capability-exchange events. | event count | gNB log — RRC/PDU control | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `pdu_setup_initiat` | `float64` | 0.00% | 7 | 1.0 / 2.0 / 3.0 | Count of logged PDU-session setup initiation events. | event count | gNB log — RRC/PDU control | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `pdu_setup_resp` | `float64` | 0.00% | 7 | 1.0 / 2.0 / 3.0 | Count of logged PDU-session setup response events. | event count | gNB log — RRC/PDU control | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `successful_rrc` | `float64` | 0.00% | 5 | 0.0 / 11.0 / 1.0 | Count of logged successful RRC connection/setup completions. | event count | gNB log — RRC/PDU control | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `ho_log` | `float64` | 0.00% | 84 | 0.0 / 17.0 / 64.0 | Feature counting log matches named `ho_log`; it appears handover-related, but the exact extractor semantics are not documented in the public dataset description. | event count | gNB log — exact extraction requires verification | Potentially relevant to `handover_count`, but must NOT be used as a direct mapping yet. | **REVIEW** |
| `mac_ul_discard_events` | `float64` | 0.00% | 1 | 0.0 | Count of logged MAC uplink discard events; this column is constant zero in the profiled file. | event count | gNB log — MAC | No direct V1 mapping; no variance in current file. | **DROP — irrelevant to V1** |
| `rrc_ue_remove` | `float64` | 0.00% | 32 | 0.0 / 1.0 / 2.0 | Count of logged UE-removal events at the RRC layer. | event count | gNB log — RRC | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `mac_ue_remove` | `float64` | 0.00% | 363 | 1.0 / 85.0 / 161.0 | Count of logged UE-removal events at the MAC layer. | event count | gNB log — MAC | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `rlc_ue_remove` | `float64` | 0.00% | 265 | 0.0 / 1.0 / 131.0 | Count of logged UE-removal events at the RLC layer. | event count | gNB log — RLC | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `ngap_initial_context_setup_response` | `float64` | 0.00% | 11 | 2.0 / 3.0 / 4.0 | Count of logged NGAP Initial Context Setup Response events. | event count | gNB log — NGAP/control plane | No direct V1 NOC KPI mapping. | **DROP — irrelevant to V1** |
| `active_pdu_session` | `int64` | 0.00% | 1 | 1 | Extracted count/state of active PDU session(s); the profiled column is constant at 1. | count | gNB log — PDU session | Not equivalent to `connected_users`; constant in current data. | **DROP — irrelevant to V1** |
| `avg_rsrp` | `float64` | 0.00% | 4221 | -96.0 / -95.96296296296296 / -95.97619047619048 | Average Reference Signal Received Power reported during the test. | dBm | gNB log — radio/MAC statistics | Strong direct reference for future `signal_quality` (prefer preserving RSRP explicitly). | **KEEP — reference KPI** |
| `avg_rsrp_meas` | `float64` | 0.00% | 2833 | 15.583333333333334 / 15.814814814814817 / 15.88095238095238 | Feature named `avg_rsrp_meas`; likely aggregates the `(N meas)` RSRP measurement-count field printed by OAI, but the exact RANalyzer extraction/aggregation is not publicly documented. | likely count | gNB log — exact extraction requires verification | No direct V1 mapping until semantics are verified. | **REVIEW** |
| `avg_snr` | `float64` | 22.94% | 4145 | 29.25 / 29.55555555555556 / 29.5 | Average Signal-to-Noise Ratio reported during the test. | dB | gNB log — radio/MAC statistics | Reference for future `signal_quality` and radio-condition modeling. | **KEEP — reference KPI** |
| `min_snr` | `float64` | 22.94% | 65 | 28.0 / 27.5 / 28.5 | Minimum observed SNR across aggregated gNB measurements for the test. | dB | gNB log — radio/MAC statistics | Optional radio-condition reference. | **KEEP — optional** |
| `max_snr` | `float64` | 22.94% | 50 | 30.0 / 31.0 / 32.0 | Maximum observed SNR across aggregated gNB measurements for the test. | dB | gNB log — radio/MAC statistics | Optional radio-condition reference. | **KEEP — optional** |
| `avg_dl_bler` | `float64` | 0.00% | 8175 | 0.0695991666666666 / 0.0557162962962962 / 0.0528378571428571 | Average downlink Block Error Rate reported by OAI MAC statistics. | ratio (0–1) | gNB log — MAC/link reliability | Radio-reliability context; not equivalent to application `packet_loss`. | **KEEP — optional** |
| `min_dl_bler` | `float64` | 0.00% | 947 | 0.00032 / 0.0 / 0.00046 | Minimum observed downlink Block Error Rate in the aggregated test. | ratio (0–1) | gNB log — MAC/link reliability | Optional radio-reliability reference. | **KEEP — optional** |
| `max_dl_bler` | `float64` | 0.00% | 4009 | 0.13067 / 0.15019 / 0.15132 | Maximum observed downlink Block Error Rate in the aggregated test. | ratio (0–1) | gNB log — MAC/link reliability | Optional radio-reliability reference. | **KEEP — optional** |
| `avg_ul_bler` | `float64` | 0.00% | 7674 | 0.0050508333333333 / 0.0031262962962962 / 0.0032309523809523 | Average uplink Block Error Rate reported by OAI MAC statistics. | ratio (0–1) | gNB log — MAC/link reliability | Radio-reliability context; not equivalent to application `packet_loss`. | **KEEP — optional** |
| `min_ul_bler` | `float64` | 0.00% | 544 | 0.0 / 0.00249 / 1e-05 | Minimum observed uplink Block Error Rate in the aggregated test. | ratio (0–1) | gNB log — MAC/link reliability | Optional radio-reliability reference. | **KEEP — optional** |
| `max_ul_bler` | `float64` | 0.00% | 2715 | 0.04489 / 0.0589 / 0.0783 | Maximum observed uplink Block Error Rate in the aggregated test. | ratio (0–1) | gNB log — MAC/link reliability | Optional radio-reliability reference. | **KEEP — optional** |
| `avg_dl_mcs0` | `float64` | 74.75% | 235 | 9.0 / 7.2 / 7.5 | Average dl MCS index for OAI log records using MCS table indicator 0. | MCS index | gNB log — MAC scheduler | High missingness in this processed file; not needed for V1. | **DROP — irrelevant to V1** |
| `min_dl_mcs0` | `float64` | 74.75% | 5 | 9.0 / 0.0 / 6.0 | Minimum dl MCS index for OAI log records using MCS table indicator 0. | MCS index | gNB log — MAC scheduler | High missingness in this processed file; not needed for V1. | **DROP — irrelevant to V1** |
| `max_dl_mcs0` | `float64` | 74.75% | 5 | 9.0 / 0.0 / 7.0 | Maximum dl MCS index for OAI log records using MCS table indicator 0. | MCS index | gNB log — MAC scheduler | High missingness in this processed file; not needed for V1. | **DROP — irrelevant to V1** |
| `avg_dl_mcs1` | `float64` | 0.00% | 4423 | 16.666666666666668 / 15.51851851851852 / 15.38095238095238 | Average dl MCS index for OAI log records using MCS table indicator 1. | MCS index | gNB log — MAC scheduler | Optional radio/scheduling context; not a core NOC KPI. | **KEEP — optional** |
| `min_dl_mcs1` | `float64` | 0.00% | 5 | 9.0 / 6.0 / 0.0 | Minimum dl MCS index for OAI log records using MCS table indicator 1. | MCS index | gNB log — MAC scheduler | Optional radio/scheduling context; not a core NOC KPI. | **KEEP — optional** |
| `max_dl_mcs1` | `float64` | 0.00% | 26 | 21.0 / 19.0 / 20.0 | Maximum dl MCS index for OAI log records using MCS table indicator 1. | MCS index | gNB log — MAC scheduler | Optional radio/scheduling context; not a core NOC KPI. | **KEEP — optional** |
| `avg_ul_mcs0` | `float64` | 74.75% | 521 | 9.0 / 7.2 / 7.5 | Average ul MCS index for OAI log records using MCS table indicator 0. | MCS index | gNB log — MAC scheduler | High missingness in this processed file; not needed for V1. | **DROP — irrelevant to V1** |
| `min_ul_mcs0` | `float64` | 74.75% | 17 | 9.0 / 0.0 / 8.0 | Minimum ul MCS index for OAI log records using MCS table indicator 0. | MCS index | gNB log — MAC scheduler | High missingness in this processed file; not needed for V1. | **DROP — irrelevant to V1** |
| `max_ul_mcs0` | `float64` | 74.75% | 27 | 9.0 / 28.0 / 0.0 | Maximum ul MCS index for OAI log records using MCS table indicator 0. | MCS index | gNB log — MAC scheduler | High missingness in this processed file; not needed for V1. | **DROP — irrelevant to V1** |
| `avg_ul_mcs1` | `float64` | 0.00% | 3462 | 25.416666666666668 / 26.296296296296298 / 26.547619047619047 | Average ul MCS index for OAI log records using MCS table indicator 1. | MCS index | gNB log — MAC scheduler | Optional radio/scheduling context; not a core NOC KPI. | **KEEP — optional** |
| `min_ul_mcs1` | `float64` | 0.00% | 20 | 11.0 / 9.0 / 12.0 | Minimum ul MCS index for OAI log records using MCS table indicator 1. | MCS index | gNB log — MAC scheduler | Optional radio/scheduling context; not a core NOC KPI. | **KEEP — optional** |
| `max_ul_mcs1` | `float64` | 0.00% | 27 | 27.0 / 28.0 / 9.0 | Maximum ul MCS index for OAI log records using MCS table indicator 1. | MCS index | gNB log — MAC scheduler | Optional radio/scheduling context; not a core NOC KPI. | **KEEP — optional** |
| `avg_nprb` | `float64` | 22.94% | 823 | 5.0 / 5.266666666666667 / 4.6875 | Average NPRB value reported with uplink MAC statistics; represents scheduled/used physical resource-block count in the OAI log context. | PRB count | gNB log — MAC scheduler | Optional radio-resource/load reference; not a required V1 KPI. | **KEEP — optional** |
| `dlsch_errors` | `float64` | 0.00% | 294 | 0.0 / 1.0 / 2.0 | Downlink shared-channel error count; OAI documents these as blocks still unsuccessful after the allowed HARQ transmissions. | count | gNB log — MAC/HARQ | Optional radio-reliability context. | **KEEP — optional** |
| `ulsch_errors` | `float64` | 0.00% | 362 | 0.0 / 1.0 / 145.0 | Uplink shared-channel error count; uplink counterpart of DLSCH errors. | count | gNB log — MAC/HARQ | Optional radio-reliability context. | **KEEP — optional** |
| `pucch0_dtx` | `float64` | 0.00% | 626 | 1.0 / 2.0 / 10.0 | Count of missed PUCCH format-0/ACK-NACK detections reported by OAI. | count | gNB log — MAC/PUCCH | Optional radio-reliability diagnostic. | **KEEP — optional** |
| `ulsch_dtx` | `float64` | 0.00% | 525 | 2.0 / 1.0 / 3.0 | Count of missed PUSCH/ULSCH detections reported by OAI. | count | gNB log — MAC/ULSCH | Optional uplink radio diagnostic. | **KEEP — optional** |
| `mac_tx` | `float64` | 0.00% | 7151 | 0.0 / 12648385.0 / 35984049.0 | Total MAC transmit-byte counter extracted from the gNB log for the test. | bytes | gNB log — MAC | Useful traffic/load reference; not automatically identical to application download traffic. | **KEEP — reference KPI** |
| `mac_rx` | `float64` | 0.00% | 7227 | 0.0 / 724693.0 / 1881257.0 | Total MAC receive-byte counter extracted from the gNB log for the test. | bytes | gNB log — MAC | Useful traffic/load reference; not automatically identical to application upload traffic. | **KEEP — reference KPI** |
| `LCID1_tx` | `float64` | 0.00% | 667 | 579.0 / 636.0 / 693.0 | MAC byte counter for Logical Channel ID 1, TX direction, aggregated for the test. | bytes | gNB log — MAC logical-channel statistics | Low-level channel-specific traffic detail; not required in V1. | **DROP — irrelevant to V1** |
| `LCID1_rx` | `float64` | 0.00% | 1394 | 1693.0 / 2111.0 / 2529.0 | MAC byte counter for Logical Channel ID 1, RX direction, aggregated for the test. | bytes | gNB log — MAC logical-channel statistics | Low-level channel-specific traffic detail; not required in V1. | **DROP — irrelevant to V1** |
| `LCID2_tx` | `float64` | 0.00% | 9 | 0.0 / 3.0 / 76.0 | MAC byte counter for Logical Channel ID 2, TX direction, aggregated for the test. | bytes | gNB log — MAC logical-channel statistics | Low-level channel-specific traffic detail; not required in V1. | **DROP — irrelevant to V1** |
| `LCID2_rx` | `float64` | 0.00% | 17 | 0.0 / 35.0 / 68.0 | MAC byte counter for Logical Channel ID 2, RX direction, aggregated for the test. | bytes | gNB log — MAC logical-channel statistics | Low-level channel-specific traffic detail; not required in V1. | **DROP — irrelevant to V1** |
| `LCID4_tx` | `float64` | 0.00% | 8152 | 12530842.0 / 37119882.0 / 75673956.0 | MAC byte counter for Logical Channel ID 4, TX direction, aggregated for the test. | bytes | gNB log — MAC logical-channel statistics | Low-level channel-specific traffic detail; not required in V1. | **DROP — irrelevant to V1** |
| `LCID4_rx` | `float64` | 0.00% | 6824 | 3517.0 / 71361.0 / 161461.0 | MAC byte counter for Logical Channel ID 4, RX direction, aggregated for the test. | bytes | gNB log — MAC logical-channel statistics | Low-level channel-specific traffic detail; not required in V1. | **DROP — irrelevant to V1** |
| `dlsch_round_0` | `float64` | 0.00% | 6120 | 1138.0 / 3361.0 / 6788.0 | Count of downlink shared channel transmissions recorded at HARQ round 0; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |
| `dlsch_round_1` | `float64` | 0.00% | 2901 | 104.0 / 273.0 / 543.0 | Count of downlink shared channel transmissions recorded at HARQ round 1; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |
| `dlsch_round_2` | `float64` | 0.00% | 596 | 1.0 / 0.0 / 8.0 | Count of downlink shared channel transmissions recorded at HARQ round 2; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |
| `dlsch_round_3` | `float64` | 0.00% | 340 | 0.0 / 1.0 / 4.0 | Count of downlink shared channel transmissions recorded at HARQ round 3; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |
| `ulsch_round_0` | `float64` | 0.00% | 5897 | 4600.0 / 10513.0 / 16432.0 | Count of uplink shared channel transmissions recorded at HARQ round 0; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |
| `ulsch_round_1` | `float64` | 0.00% | 2190 | 4.0 / 16.0 / 32.0 | Count of uplink shared channel transmissions recorded at HARQ round 1; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |
| `ulsch_round_2` | `float64` | 0.00% | 431 | 0.0 / 1.0 / 4.0 | Count of uplink shared channel transmissions recorded at HARQ round 2; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |
| `ulsch_round_3` | `float64` | 0.00% | 390 | 0.0 / 1.0 / 4.0 | Count of uplink shared channel transmissions recorded at HARQ round 3; round 0 is the initial transmission and rounds 1–3 represent retransmission stages. | transmission count | gNB log — MAC/HARQ | Optional radio-reliability feature; can later derive retransmission ratios. | **KEEP — optional** |

---

## 5. Final Mapping to Our NOC Schema

| Future NOC field | RANalyzer support | Step 6 decision |
|---|---|---|
| `timestamp` | `log_id` encodes `YYYYMMDD_HHMMSS` | **DERIVE from `log_id`** |
| `cell_id` | No multi-cell operator identifier suitable for our scenario | **Synthetic** |
| `region` | Not available | **Synthetic** |
| `location_type` | Not available | **Synthetic** |
| `technology` | Dataset is a private 5G/OAI environment | **Project metadata / simulator-defined** |
| `connected_users` | No suitable direct field | **Synthetic** |
| `download_traffic` | `total_bytes`, target rate and MAC TX can inform behavior | **Real-data-informed simulation** |
| `upload_traffic` | Tests are primarily downlink; no equivalent application upload KPI | **Synthetic** |
| `throughput` | `avg_throughput_mbps` | **Direct real reference** |
| `latency` | No direct processed latency field | **Synthetic or later external reference** |
| `packet_loss` | `avg_packet_loss_percent` | **Direct real reference** |
| `signal_quality` | `avg_rsrp`, plus SNR context | **Direct real reference** |
| `cpu_usage` | Raw source includes CPU, but no direct CPU column is present in this processed profile | **Synthetic for V1 unless raw CPU is extracted later** |
| `memory_usage` | Not available | **Synthetic** |
| `handover_count` | `ho_log` is not sufficiently documented for direct use | **Synthetic for V1; `ho_log` remains REVIEW** |

---

## 6. Recommended Real Reference Feature Set for Step 7/EDA

For the first Kaggle analysis, start with a deliberately small feature set:

```text
log_id
git_hash
target_rate_mbps
avg_throughput_mbps
avg_jitter_ms
avg_packet_loss_percent
throughput_efficiency_percent
total_bytes
avg_rsrp
avg_snr
avg_dl_bler
avg_ul_bler
avg_nprb
dlsch_errors
ulsch_errors
mac_tx
mac_rx
dlsch_round_0
dlsch_round_1
ulsch_round_0
ulsch_round_1
```

Do **not** start with all 84 features.

The purpose of the first real-data EDA is to understand:

```text
Offered Load
     ↓
Throughput

Signal Conditions
     ↓
Throughput / Packet Loss

Radio Reliability
     ↓
Performance

Traffic Volume
     ↓
Network Behavior
```

rather than to maximize the number of columns used.

---

## 7. Features to Exclude From the Initial ML/EDA Core

For the first Version 1 study, do not make the following groups core ML
features:

- `log_id` as a raw numeric/string predictor
- `git_hash` as a normal numerical predictor
- constant metadata such as `protocol_stack` and `flow_type`
- Random Access event counters
- RRC/PDU/NGAP event counters
- UE-removal counters
- LCID-specific byte counters
- `*_mcs0` fields with 74.75% missingness
- `ho_log` until verified

Some of these may be studied later, but adding all of them now would increase
complexity without helping our main learning goal.

---

## 8. Important Terminology Notes

### BLER is not packet loss

`avg_dl_bler` and `avg_ul_bler` are radio-link Block Error Rate measurements.
They must **not** be renamed as application/network packet loss.

### MAC bytes are not automatically application traffic

`mac_tx` and `mac_rx` are MAC-layer counters. They can inform traffic/load
behavior, but they should not be silently renamed to
`download_traffic`/`upload_traffic`.

### RSRP and SNR are different

`avg_rsrp` represents received reference-signal power, while `avg_snr`
represents signal relative to noise. Both can inform radio quality but should
remain separate measurements during analysis.

### Throughput efficiency is derived

The RANalyzer paper defines throughput efficiency using measured throughput
relative to requested/target throughput. It is useful for performance
analysis but is not an independent raw measurement.

---

## 9. Source-Supported Interpretation

The public RANalyzer documentation states that raw iPerf3 data includes:

- throughput,
- jitter,
- packet loss,
- transferred bytes,
- CPU utilization,
- traffic flow type,
- target bitrate.

The processed CSV combines aggregated iPerf3 measurements with features from
the gNB logs.

OpenAirInterface's MAC documentation supports interpretation of the low-level
radio columns used here, including:

- RSRP and SNR,
- DLSCH/ULSCH BLER,
- MCS,
- NPRB,
- DLSCH/ULSCH error counts,
- PUCCH/ULSCH DTX,
- MAC and LCID byte counters,
- DLSCH/ULSCH HARQ transmission rounds.

For uncertain extractor-specific fields, this document deliberately uses
**REVIEW** rather than claiming an unsupported meaning.

---

## 10. References

1. RANalyzer Dataset  
   https://github.com/wineslab/RANalyzer-Dataset

2. Shirkhani, R., Prasad, R., Bonati, L., Melodia, T., & Polese, M.,
   *RANalyzer: Automated Continuous RAN Software Evaluation and Regression
   Analysis*, IEEE NetSoft 2026 / arXiv:2604.23153.  
   https://arxiv.org/abs/2604.23153

3. OpenAirInterface MAC Usage Documentation  
   https://github.com/OPENAIRINTERFACE/openairinterface5g/blob/develop/doc/MAC/mac-usage.md

---

## 11. Step 6 Completion Checklist

- [x] Exact processed columns extracted
- [x] Pandas data types recorded
- [x] Missing-value percentages recorded
- [x] Example values recorded
- [x] Main feature meanings documented
- [x] Units documented where defensible
- [x] Source/layer identified
- [x] NOC mappings defined
- [x] KEEP / DROP / REVIEW decisions assigned
- [x] Unsupported mappings explicitly avoided
- [x] Core real-data reference features selected
- [x] Synthetic-only V1 features identified

**Step 6 is complete.**

---

## 12. Next Step

The next project step should be to move the real processed dataset into
**Kaggle** and perform the first controlled dataset inspection/EDA.

The first Kaggle notebook should focus on:

```text
Dataset structure
        ↓
Data quality
        ↓
Core KPI distributions
        ↓
Missingness
        ↓
KPI relationships
        ↓
Realistic ranges for simulator design
```

Machine-learning training should still wait until we understand these real
measurements properly.
