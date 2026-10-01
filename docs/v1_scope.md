# Telecom Network Monitoring & Anomaly Detection System

## Version 1 Project Scope

## 1. Project Goal

The goal of Version 1 is to build a beginner-friendly, end-to-end telecom network monitoring application that combines:

* Telecommunications
* Python
* Data analysis
* Machine learning
* SQL/PostgreSQL
* REST API development
* React frontend development
* Software engineering
* Docker

The system will simulate a simplified telecom **Network Operations Center (NOC)**.

It will monitor cellular-network Key Performance Indicators (KPIs), detect abnormal network behavior, explain which KPIs are unusual, store the results, and visualize them through a web dashboard.

---

# 2. Main System Flow

The complete Version 1 system will follow this pipeline:

```text
Public Real 5G Dataset
        ↓
Kaggle Analysis
        ↓
Understand Real KPI Behavior
        ↓
Real-Data-Informed Telecom Simulator
        ↓
20 Simulated Telecom Cells
        ↓
Normal + Injected Anomaly Data
        ↓
Data Preprocessing
        ↓
Feature Engineering
        ↓
Statistical Baseline
        ↓
Isolation Forest
        ↓
Anomaly Detection
        ↓
Severity Calculation
        ↓
KPI-Based Explanation
        ↓
PostgreSQL
        ↓
FastAPI REST API
        ↓
React NOC Dashboard
        ↓
Near-Real-Time Monitoring
```

---

# 3. Data Strategy

Version 1 will use two types of data.

## 3.1 Public Real 5G Data

A public 5G measurement dataset will first be analyzed in Kaggle.

The initial dataset will be:

**RANalyzer 5G Dataset**

The real dataset will help us understand realistic values and relationships for KPIs such as:

* Throughput
* Packet loss
* CPU utilization
* Signal quality
* Traffic-related measurements

The public dataset will mainly be used as a **reference for realistic telecom behavior**.

---

## 3.2 Synthetic NOC Dataset

Because a public dataset containing every KPI required for our complete NOC application is not available, we will create our own multi-cell telecom dataset.

The simulator will generate approximately:

```text
20 cells

14 days

15-minute measurement intervals
```

The simulated data will contain both:

```text
Normal behavior
+
Controlled abnormal behavior
```

The simulator will be informed by observations from real public telecom data wherever possible.

---

# 4. Simulated Network

Version 1 will simulate approximately 20 4G/5G-style cells.

Example cell IDs:

```text
CTG_001
CTG_002
CTG_003
...
CTG_020
```

Each cell will have a simulated location type such as:

```text
Residential
Business
University
Transport
Suburban
```

Different cell types will have different daily traffic patterns.

---

# 5. Network KPIs

The Version 1 monitoring system will use the following main KPIs:

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

Additional metadata:

```text
timestamp
cell_id
region
location_type
technology
```

---

# 6. Network Behavior

The simulator should create realistic relationships between KPIs.

For example:

```text
Connected Users ↑
       ↓
Traffic Demand ↑
       ↓
Network Load ↑
       ↓
CPU Usage ↑
       ↓
Possible Congestion
       ↓
Latency ↑
Packet Loss ↑
Throughput/User ↓
```

These relationships will be probabilistic and simplified.

The project will not claim to reproduce the complete behavior of a commercial cellular network.

---

# 7. Anomaly Types

Version 1 will support controlled anomaly scenarios such as:

1. Latency spike
2. Packet-loss spike
3. Throughput degradation
4. Unusual traffic surge
5. CPU overload
6. Memory overload
7. Multi-KPI degradation
8. Temporary anomaly
9. Persistent anomaly

Each injected anomaly will have a known ground-truth label.

---

# 8. Machine Learning

## Statistical Baseline

Before machine learning, a simple anomaly detector will be implemented using techniques such as:

```text
Rolling statistics
Percentage deviation
Z-score
Historical baseline deviation
```

This will provide a baseline for comparison.

---

## Main ML Model

The main Version 1 machine-learning model will be:

**Isolation Forest**

It will perform unsupervised anomaly detection.

Ground-truth anomaly labels will be used only for evaluation, not as model input.

---

# 9. ML Development Platform

All major ML experimentation will be performed using:

**Kaggle**

Kaggle will be used for:

```text
Real dataset analysis

EDA

Data preprocessing experiments

Feature engineering

Statistical anomaly detection

Isolation Forest training

Model evaluation

Model comparison

Model export
```

The trained model will later be downloaded and integrated into the local application.

---

# 10. Model Evaluation

The anomaly-detection system will be evaluated using:

```text
Precision

Recall

F1-score

Confusion Matrix

Detection Rate

False Positive Rate

False Alarms per Cell per Day

Detection Delay
```

Performance should also be examined separately for different anomaly types.

---

# 11. Feature Engineering

Version 1 will include features such as:

```text
total_traffic

traffic_per_user

latency_change

packet_loss_change

throughput_change

traffic_change

rolling_mean

rolling_standard_deviation

cell-specific historical baseline

KPI deviation from baseline
```

Temporal features must be calculated without using future information.

---

# 12. Explainability

The system will explain detected anomalies using measurable KPI deviations.

Example:

```text
Cell: CTG_102

Severity: HIGH

Packet Loss
Current: 8.7%
Baseline: 0.9%
Deviation: +867%

Latency
Current: 180 ms
Baseline: 36 ms
Deviation: +400%

Throughput
Current: 45 Mbps
Baseline: 91 Mbps
Deviation: -51%
```

Version 1 will not require advanced SHAP-based explainability.

---

# 13. Severity

The monitoring system will use:

```text
NORMAL
WARNING
HIGH
CRITICAL
```

Severity will be determined separately from anomaly detection.

It may consider:

```text
Anomaly score

+

Magnitude of KPI deviations

+

Number of affected KPIs

+

Persistence
```

---

# 14. Backend

The backend will use:

```text
Python
FastAPI
Pydantic
SQLAlchemy
```

Main responsibilities:

* Validate requests
* Access PostgreSQL
* Load the trained ML model
* Run predictions
* Calculate severity
* Generate explanations
* Return JSON responses
* Handle errors

---

# 15. Database

The database will use:

**PostgreSQL**

Initial tables:

```text
cells

network_metrics

anomalies
```

The database will store both historical measurements and detected anomaly events.

---

# 16. REST API

Initial endpoints:

```text
GET  /health

GET  /cells

GET  /cells/{cell_id}

GET  /cells/{cell_id}/metrics

GET  /anomalies

GET  /anomalies/{id}

GET  /statistics

POST /predict

GET  /model/info
```

---

# 17. Frontend

The dashboard will use:

```text
React
JavaScript
Recharts or Plotly
```

The UI should resemble a simplified telecom NOC dashboard.

---

# 18. Dashboard Features

The main dashboard will display:

```text
Total Cells

Healthy Cells

Warning Cells

High Anomaly Cells

Critical Cells

Average Latency

Average Throughput

Average Packet Loss
```

It will also contain:

* KPI time-series graphs
* Active anomaly table
* Cell search/filtering
* Cell detail page
* Anomaly detail view

---

# 19. Cell Detail Page

Users should be able to inspect one cell and view:

```text
Cell information

Current KPIs

Current status

Historical KPI trends

Recent anomalies

Baseline comparisons
```

---

# 20. Near-Real-Time Monitoring

After the batch system works, the telecom simulator will continuously generate new observations.

Pipeline:

```text
New KPI Observation
        ↓
Preprocessing
        ↓
Feature Engineering
        ↓
Isolation Forest
        ↓
Severity
        ↓
Explanation
        ↓
PostgreSQL
        ↓
FastAPI
        ↓
React Dashboard
```

The React dashboard will initially use normal HTTP polling every few seconds.

Kafka and WebSockets are not required for Version 1.

---

# 21. Local Development

The final software application will be developed locally using:

```text
VS Code

Python

PostgreSQL

FastAPI

React

Git

GitHub
```

Kaggle will be used mainly for data analysis and ML experimentation.

---

# 22. Deployment

Version 1 will use:

```text
Docker
Docker Compose
```

The final system should contain separate containers for:

```text
Frontend
Backend
PostgreSQL
```

The application should eventually start using:

```bash
docker compose up
```

---

# 23. Testing

Version 1 will include basic tests for:

* Data generation
* Feature engineering
* Input validation
* ML model loading
* ML prediction
* Severity calculation
* Explanation generation
* API endpoints

A key integration test will verify that:

```text
Kaggle prediction
=
Local application prediction
```

for the same observation.

---

# 24. Version 1 Technology Stack

## Data and ML

```text
Python
NumPy
Pandas
Scikit-learn
Matplotlib
Plotly
Kaggle
```

## Backend

```text
FastAPI
Pydantic
SQLAlchemy
Uvicorn
```

## Database

```text
PostgreSQL
```

## Frontend

```text
React
JavaScript
Recharts / Plotly
```

## Software Engineering

```text
Git
GitHub
Pytest
Logging
Environment Variables
```

## Deployment

```text
Docker
Docker Compose
```

---

# 25. Version 1 Non-Goals

The following technologies/features are intentionally excluded from Version 1:

```text
Kafka
Redis
Kubernetes
Airflow
MLflow
LSTM
Transformer
Autoencoder
Microservices
SHAP
Authentication
Role-Based Access Control
Email alerts
Slack alerts
Advanced root-cause analysis
Advanced cloud architecture
```

They may be added in Version 2.

---

# 26. Important Scientific Limitation

The final 20-cell monitoring dataset will be primarily synthetic.

Public real-world 5G measurements will be used to understand and calibrate realistic KPI behavior where possible.

The project must clearly distinguish:

```text
Real public measurements

vs

Synthetic telecom monitoring data
```

The system detects statistical anomalies.

It does not prove the physical root cause of network problems.

For example, it may say:

> Latency and packet loss are significantly above the historical baseline while throughput has decreased.

It should not automatically claim:

> Antenna failure detected.

---

# 27. Final Version 1 Deliverables

At project completion there should be:

```text
1. Professional GitHub Repository

2. Real 5G Dataset Analysis Notebook

3. Main Kaggle ML Notebook

4. Telecom KPI Simulator

5. Generated NOC Dataset

6. Statistical Baseline

7. Trained Isolation Forest Model

8. Model Evaluation Results

9. Explanation Engine

10. Severity Engine

11. PostgreSQL Database

12. FastAPI Backend

13. React Dashboard

14. Near-Real-Time Simulator

15. Automated Tests

16. Docker Setup

17. Architecture Diagram

18. Dashboard Screenshots

19. Professional README

20. Kaggle Notebook Link
```

---

# 28. Definition of Done

Version 1 is complete when the following flow works successfully:

```text
Simulated Telecom Cell
          ↓
New KPI Measurement
          ↓
Preprocessing
          ↓
Feature Engineering
          ↓
Isolation Forest
          ↓
Normal / Anomaly Prediction
          ↓
Severity Calculation
          ↓
KPI Explanation
          ↓
PostgreSQL Storage
          ↓
FastAPI
          ↓
React Dashboard
          ↓
User Investigates the Cell
```

The project should not be considered complete simply because the ML model has been trained.

The complete end-to-end software system must work.

---

# 29. Main Learning Objective

The purpose of Version 1 is not to use the largest number of technologies.

The goal is to be able to:

```text
UNDERSTAND
      +
BUILD
      +
TEST
      +
DEBUG
      +
EXPLAIN
      +
DEMONSTRATE
```

one complete software project.

After completing Version 1, I should be able to explain what every major component does and why it exists.
