from pathlib import Path
import pandas as pd

INPUT = Path("data/external/ranalyzer/processed-dataset.csv")
PROFILE_OUT = Path("data/sample/ranalyzer_column_profile.csv")
MD_OUT = Path("docs/ranalyzer_data_dictionary.md")

if not INPUT.exists():
    raise FileNotFoundError(
        f"Dataset not found: {INPUT}\n"
        "Complete Step 5 first and make sure processed-dataset.csv is in the expected folder."
    )

df = pd.read_csv(INPUT)

print("=" * 70)
print("RANalyzer processed dataset profile")
print("=" * 70)
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")
print()

rows = []
for col in df.columns:
    s = df[col]
    non_null = int(s.notna().sum())
    missing = int(s.isna().sum())
    missing_pct = round((missing / len(df) * 100), 2) if len(df) else 0.0
    unique = int(s.nunique(dropna=True))

    samples = (
        s.dropna()
        .astype(str)
        .drop_duplicates()
        .head(3)
        .tolist()
    )

    rows.append(
        {
            "column": col,
            "dtype": str(s.dtype),
            "non_null": non_null,
            "missing": missing,
            "missing_pct": missing_pct,
            "unique_values": unique,
            "sample_values": " | ".join(samples),
        }
    )

profile = pd.DataFrame(rows)

PROFILE_OUT.parent.mkdir(parents=True, exist_ok=True)
profile.to_csv(PROFILE_OUT, index=False)

MD_OUT.parent.mkdir(parents=True, exist_ok=True)

header = """# RANalyzer Processed Dataset — Data Dictionary

## Purpose

This document describes the columns in the local `processed-dataset.csv`
used as a real 5G measurement reference for the Telecom Network Monitoring
& Anomaly Detection System.

The initial table below is generated directly from the downloaded CSV so
that column names, data types, missing values, and examples are based on
the actual file rather than assumptions.

## Dataset Summary

- Source: RANalyzer Dataset
- Local file: `data/external/ranalyzer/processed-dataset.csv`
- Unit of observation: one aggregated 5G test run
- Identifier documented by the source: `log_id`
- Real-data purpose in this project: understand realistic KPI distributions
  and relationships before designing the synthetic multi-cell NOC simulator.

## Important Rule

Do not assign a meaning or unit to a processed feature unless it can be
supported by the official dataset documentation, paper, raw-field
definition, or clearly derived formula.

## Column Dictionary

| Column | Pandas dtype | Missing % | Unique | Example values | Meaning | Unit | Source / layer | NOC mapping | Decision |
|---|---|---:|---:|---|---|---|---|---|---|
"""

lines = [header]

for _, r in profile.iterrows():
    examples = str(r["sample_values"]).replace("|", "/").replace("\n", " ")
    lines.append(
        f'| `{r["column"]}` | `{r["dtype"]}` | {r["missing_pct"]:.2f}% | '
        f'{r["unique_values"]} | {examples} | TODO | TODO | TODO | TODO | TODO |\n'
    )

footer = """
## Decision Values

Use one of the following in the **Decision** column:

- **KEEP — reference KPI**: useful for studying real network behavior.
- **KEEP — metadata**: useful for identifying or grouping tests.
- **KEEP — optional**: potentially useful but not required for Version 1.
- **DERIVED**: calculated from other fields.
- **DROP — identifier only**: not useful as an ML feature.
- **DROP — leakage/risk**: should not be used as an ML input.
- **DROP — irrelevant to V1**: valid field but outside current scope.
- **REVIEW**: meaning is not yet sufficiently supported.

## Main NOC Features We Eventually Want to Map

Our Version 1 application schema is:

- `timestamp`
- `cell_id`
- `region`
- `location_type`
- `technology`
- `connected_users`
- `download_traffic`
- `upload_traffic`
- `throughput`
- `latency`
- `packet_loss`
- `signal_quality`
- `cpu_usage`
- `memory_usage`
- `handover_count`

Not every application feature needs to exist in RANalyzer.

The correct mapping may therefore be:

- direct mapping,
- real-data-informed simulation,
- or fully synthetic.

## Officially Documented Source Concepts

The RANalyzer source documentation describes the following raw measurement
families:

### iPerf3 / end-to-end performance

- Throughput (`bits_per_second`)
- Jitter (`jitter_ms`)
- Lost packets
- Total packets
- Packet loss (`lost_percent`)
- Bytes transferred
- Host CPU utilization
- Remote CPU utilization
- Traffic flow type
- Target traffic rate (`target_rate_mbps`)
- Date / time identifiers

### gNB radio and protocol measurements

- RSRP
- SNR / channel-quality indicators
- BLER
- MCS
- HARQ retransmission statistics
- MAC/RLC byte counters
- RRC events
- PDU-session events
- Random-access events
- Warnings / error patterns

The processed CSV aggregates/extracts features from these sources at
test-run level. Exact processed-column semantics must be verified before
filling the TODO fields above.

## Mapping Strategy for Our Project

### Likely direct or reference mappings

- Real measured throughput -> informs `throughput`
- Packet-loss measurements -> informs `packet_loss`
- RSRP/SNR-type measurements -> informs `signal_quality`
- CPU measurements -> informs `cpu_usage`
- Bytes / target rate / load metrics -> inform traffic/load relationships

### Likely synthetic features

Unless a directly suitable field is present and documented:

- `cell_id`
- `region`
- `location_type`
- `connected_users`
- `memory_usage`
- `handover_count`

These should remain explicitly synthetic in our NOC simulator.

## Next Action

After generating this file, review the exact column names and fill the
Meaning / Unit / Source / NOC mapping / Decision fields using the official
dataset README and paper. Unknown columns should remain **REVIEW** rather
than being guessed.
"""

lines.append(footer)
MD_OUT.write_text("".join(lines), encoding="utf-8")

print(profile.to_string(index=False))
print()
print(f"Saved profile: {PROFILE_OUT}")
print(f"Saved dictionary template: {MD_OUT}")
