# Step 6 — Build the RANalyzer Data Dictionary

## Goal

Create an exact inventory of every column in the downloaded
`processed-dataset.csv`, understand which measurements are useful for our
project, and map supported real measurements to the future synthetic NOC
schema.

This step is deliberately completed **before EDA or ML**.

---

## 1. Why a data dictionary is necessary

The processed RANalyzer CSV contains aggregated features from several
sources. A column name alone is not enough to safely assume:

- what the value means,
- what unit it uses,
- whether it comes from iPerf3 or the gNB,
- whether it is an identifier, KPI, KPM, event count, or derived feature,
- or whether it should be used by a machine-learning model.

The official repository documents the raw measurement families and states
that the processed file contains aggregated iPerf3 metrics plus gNB signal
quality and protocol-event features. It does not provide a complete
processed-column dictionary.

Therefore we first profile the actual local CSV.

---

## 2. Files created in this step

Add:

```text
scripts/
└── profile_ranalyzer.py
```

Running it creates:

```text
data/sample/
└── ranalyzer_column_profile.csv

docs/
└── ranalyzer_data_dictionary.md
```

The raw external dataset remains ignored by Git.

---

## 3. Run the profiler

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\profile_ranalyzer.py
```

The script prints:

- row count,
- column count,
- each exact column name,
- Pandas data type,
- missing-value count and percentage,
- unique-value count,
- a few example values.

It also creates a Markdown data-dictionary template using the **real
columns from your file**.

---

## 4. Inspect the generated files

Open:

```text
data/sample/ranalyzer_column_profile.csv
```

and:

```text
docs/ranalyzer_data_dictionary.md
```

The Markdown table includes columns for:

```text
Column
Pandas dtype
Missing %
Unique values
Example values
Meaning
Unit
Source / layer
NOC mapping
Decision
```

The first five fields are generated automatically.

The semantic fields remain `TODO` until they are verified.

---

## 5. Source-supported concepts

According to the RANalyzer dataset documentation, raw iPerf3 data includes:

- bytes transferred,
- throughput (`bits_per_second`),
- jitter (`jitter_ms`),
- lost packets,
- total packets,
- packet-loss percentage,
- host CPU utilization,
- remote CPU utilization,
- traffic flow type,
- target bitrate,
- date/time identifiers.

The gNB logs contain measurements/events including:

- RSRP,
- SNR/channel quality,
- BLER,
- MCS,
- HARQ retransmissions,
- MAC/RLC byte counters,
- RRC events,
- PDU-session events,
- random-access events,
- warnings/error patterns.

The processed dataset aggregates/extracts these at test-run level.

---

## 6. Map to our NOC schema

For each real processed feature, decide whether it helps inform:

```text
throughput
packet_loss
signal_quality
cpu_usage
network traffic/load
```

Do not force mappings for fields that are not equivalent.

For example:

```text
RSRP
```

may inform our simplified:

```text
signal_quality
```

but `RSRP` should still be documented as RSRP with its own unit and meaning.

Features such as:

```text
connected_users
memory_usage
handover_count
region
location_type
```

may remain synthetic if the real dataset does not provide a suitable
documented equivalent.

---

## 7. Classification rule

Use these decisions:

```text
KEEP — reference KPI
KEEP — metadata
KEEP — optional
DERIVED
DROP — identifier only
DROP — leakage/risk
DROP — irrelevant to V1
REVIEW
```

If you do not know exactly what a field means, use:

```text
REVIEW
```

Never guess.

---

## 8. Git check

The large external CSV should still be ignored.

Run:

```powershell
git status
```

You should see the new script/documentation files, but not:

```text
data/external/ranalyzer/processed-dataset.csv
```

---

## 9. Commit

After the generated data dictionary has been reviewed:

```powershell
git add scripts/profile_ranalyzer.py
git add docs/ranalyzer_data_dictionary.md
git add data/sample/ranalyzer_column_profile.csv

git commit -m "docs: profile RANalyzer dataset columns"
git push
```

The small column-profile CSV is safe and useful to keep in the repository.

---

## 10. Completion condition

Step 6 is complete when:

- the exact processed CSV columns are extracted,
- data types are known,
- missingness is recorded,
- sample values are visible,
- every feature has a documented or REVIEW status,
- useful real KPIs are mapped to the future NOC schema,
- unsupported features are not guessed,
- the large original CSV is still excluded from Git.

Only after this should we begin detailed Kaggle inspection and EDA.
