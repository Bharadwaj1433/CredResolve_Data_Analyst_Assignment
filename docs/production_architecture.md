# CredResolve Production Analytics Architecture

## 1. Architecture Objective

The CredResolve production analytics architecture provides a controlled path from operational collection data to reliable analytical evidence and business decisions.

The architecture is designed around one core principle:

> Raw operational data should not directly drive recovery metrics or business decisions.

Instead, data passes through controlled layers where it is ingested, validated, cleaned, standardized, consolidated, and transformed into governed analytical metrics.

The architecture supports the complete analytical workflow used in this assignment:

- Business performance reconstruction
- Data-quality investigation
- Payment attribution
- Portfolio and DPD analysis
- Campaign and channel analysis
- Driver analysis
- Statistical investigation
- Counterfactual analysis
- 11% improvement verification
- Investment analysis
- Executive reporting

The architecture separates operational data processing from analytical interpretation. This prevents data-quality problems, inconsistent definitions, and uncontrolled transformations from directly affecting executive conclusions.

---

## 2. Architecture Principles

### 2.1 Source Preservation

Original operational records are preserved in the Raw/Landing layer before analytical transformations are applied.

This provides traceability between the source record and the final analytical result.

### 2.2 Controlled Transformation

Data moves through Staging, Quality, Clean, and Golden layers.

Each layer has a specific responsibility rather than combining ingestion, cleaning, and business logic into a single transformation.

### 2.3 Account-Centric Analysis

`account_id` is the canonical analytical entity for recovery analysis.

The accepted payment attribution path is:

`payment_id → account_id`

Borrower information remains available as a secondary relationship attribute.

### 2.4 Governed Metrics

Recovery metrics are calculated from a controlled analytical layer using documented definitions and denominators.

Metrics that cannot be reliably validated from the supplied data are explicitly classified as unavailable or unverified.

### 2.5 Reproducibility

Transformations and analytical calculations are implemented through reproducible SQL, Python analysis scripts, and the Golden analytical layer.

The same source data and transformation logic should produce the same analytical result.

### 2.6 Production Controls

Data quality, governance, monitoring, and orchestration are treated as production controls surrounding the analytical pipeline rather than as independent analytical outputs.

---

<div style="page-break-after: always;"></div>

# 3. Architecture Overview

The CredResolve architecture follows five primary stages:

**Data Sources → Acquire → Manage → Analyse & Visualise → Business Decision**

```mermaid
flowchart LR

    subgraph SOURCES["DATA SOURCES"]
        direction TB

        A1[("Accounts")]
        A2[("Borrowers")]
        A3[("Payments")]
        A4[("Calls")]
        A5[("Campaigns")]
        A6[("Agents / Vendors")]
        A7[("Collection Events")]
    end


    subgraph ACQUIRE["ACQUIRE"]
        direction TB

        B1["Data Ingestion"]
        B2["Batch Loads"]
        B3["Incremental Loads"]

        B1 --> B2
        B1 --> B3
    end


    subgraph MANAGE["MANAGE"]
        direction TB

        C1[("RAW / LANDING")]
        C2["STAGING"]
        C3{"QUALITY<br/>GATE"}
        C4["CLEAN<br/>LAYER"]
        C5[("GOLDEN<br/>LAYER")]

        C1 --> C2
        C2 --> C3
        C3 -->|PASS| C4
        C4 --> C5
    end


    subgraph ANALYSE["ANALYSE & VISUALISE"]
        direction TB

        D1["FEATURE<br/>LAYER"]
        D2["GOVERNED<br/>METRICS"]
        D3["ANALYTICAL<br/>INVESTIGATION"]
        D4[/"EXECUTIVE<br/>DASHBOARD"/]
        D5[/"EXECUTIVE<br/>REPORT"/]

        D1 --> D2
        D2 --> D3
        D3 --> D4
        D3 --> D5
    end


    subgraph DECISION["BUSINESS DECISION"]
        direction TB

        E1["KEY<br/>FINDINGS"]
        E2["RECOMMENDATIONS"]
        E3["₹10 Cr<br/>INVESTMENT<br/>DECISION"]

        E1 --> E2
        E2 --> E3
    end


    SOURCES --> ACQUIRE
    ACQUIRE --> MANAGE
    MANAGE --> ANALYSE
    ANALYSE --> DECISION


    subgraph CONTROLS["CROSS-CUTTING PRODUCTION CONTROLS"]
        direction LR

        F1["DATA QUALITY"]
        F2["GOVERNANCE"]
        F3["MONITORING"]
        F4["ORCHESTRATION"]
    end


    CONTROLS -.-> MANAGE
    CONTROLS -.-> ANALYSE


    classDef source fill:#EAF2F8,stroke:#2F5597,stroke-width:2px,color:#17202A;
    classDef acquire fill:#FFF2CC,stroke:#BF9000,stroke-width:2px,color:#17202A;
    classDef manage fill:#E2F0D9,stroke:#548235,stroke-width:2px,color:#17202A;
    classDef quality fill:#FCE4D6,stroke:#C65911,stroke-width:2px,color:#17202A;
    classDef analysis fill:#EDE7F6,stroke:#674EA7,stroke-width:2px,color:#17202A;
    classDef output fill:#D9EAF7,stroke:#1F4E78,stroke-width:2px,color:#17202A;
    classDef decision fill:#E2F0D9,stroke:#548235,stroke-width:2px,color:#17202A;
    classDef control fill:#F2F2F2,stroke:#666666,stroke-width:2px,color:#17202A;

    class A1,A2,A3,A4,A5,A6,A7 source;
    class B1,B2,B3 acquire;
    class C1,C2,C4,C5 manage;
    class C3 quality;
    class D1,D2,D3 analysis;
    class D4,D5 output;
    class E1,E2,E3 decision;
    class F1,F2,F3,F4 control;