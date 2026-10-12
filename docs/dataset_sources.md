# Dataset Sources

## RANalyzer Dataset

**Dataset:** RANalyzer — Automated Continuous RAN Software Evaluation and Regression Analysis

**Source:**  
https://github.com/wineslab/RANalyzer-Dataset

**Initial file used:**

`processed-dataset.csv`

## Purpose in This Project

The RANalyzer dataset is used as a real-world 5G measurement reference for understanding network KPI distributions and relationships.

The final multi-cell NOC dataset used by this project will be synthetic, but selected KPI behavior will be informed by observations from public real-world measurements where appropriate.

## Dataset Characteristics

The dataset contains end-to-end 5G measurements collected from a private 5G testbed.

The processed dataset contains aggregated features derived from:

- iPerf3 measurements
- gNB logs
- Radio measurements
- Network performance measurements
- CPU utilization measurements

Relevant measurements include concepts such as:

- Throughput
- Packet loss
- Jitter
- CPU utilization
- RSRP
- SNR
- BLER
- MCS
- HARQ retransmissions

## License

CC BY 4.0.

## Citation

R. Shirkhani, R. Prasad, L. Bonati, T. Melodia, and M. Polese,  
"RANalyzer: Automated Continuous RAN Software Evaluation and Regression Analysis,"  
IEEE International Conference on Network Softwarization (NetSoft), 2026.

## Important Note

This dataset is not presented as commercial telecom-operator NOC data.

It comes from a controlled private 5G testbed and is used in this project as a real measurement reference.