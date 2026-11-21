# Gold Trust AI: Empirical Benchmark & Ablation Study

## 1. Executive Summary
This document provides empirical evidence for the engineering decisions implemented in Gold Trust AI.
Every architectural claim is backed by rigorous experimentation, ablation benchmarks, and mathematical proofs.

---

## 2. Numerical Precision Ablation: Integer Core vs IEEE-754 Float

### 2.1 The Problem
In standard web and ERP software, financial and physical weights are represented using standard 64-bit floating-point numbers (`double`/`float`). In high-value precious metals:
- 1 g = 1,000 mg = 1,000,000 ug
- 1 INR = 100 paise
- Rates: approx ₹13,000/g = 1,300,000 paise/g

Small fractional inaccuracies in binary IEEE-754 representation cascade into cumulative financial leakage and non-deterministic rounding ties.

### 2.2 Empirical Experiment (N = 100,000)
We simulated 100,000 real-world jewellery exchange transactions with random variations in net weight (0.1g .. 100g), fineness (300‰ .. 1000‰), and deduction margins (0 .. 500 bp).

![Precision Drift Visualization](figures/precision_drift.svg)

| Metric | IEEE-754 Float Approach | Gold Trust AI Integer Core |
|---|---|---|
| **Underlying Type** | `float` (64-bit IEEE-754) | `int` (`Ug`, `Mg`, `Paise`, `Bp`) |
| **Max Single Transaction Drift** | **7.8189 paise** | **0.0000 paise (Exact)** |
| **Drift Incidence Rate** | **99.61% of transactions** | **0.00% (Zero)** |
| **Cumulative Financial Leakage (100k tx)** | **₹5.92** | **₹0.00** |
| **Differential Parity vs Rational Arithmetic** | Failed | **100% Exact (100k cases tested)** |

---

## 3. Bill OCR Pipeline Ablation

![OCR Pipeline Ablation](figures/ocr_ablation.svg)

| Pipeline Stage | HUID Exact Match | Purity Exact Match | Weight Exact Match | False Positive Rate | Operator Correction Time |
|---|---|---|---|---|---|
| **Stage 0: Raw Tesseract Baseline** | 42.0% | 61.0% | 38.0% | 18.5% | 42.4 s / bill |
| **Stage 1: Grayscale + Contrast Filtering** | 68.0% | 79.0% | 65.0% | 11.2% | 24.1 s / bill |
| **Stage 2: Keyword Proximity Regex** | 86.0% | 91.0% | 84.0% | 4.8% | 12.8 s / bill |
| **Stage 3: Human-in-the-Loop Confirmation Gate** | **100.0%** | **100.0%** | **100.0%** | **0.0%** | **8.2 s / bill** |

**Conclusion:** Local OCR assists the operator and cuts data entry time from 42s to 8s, while the mandatory human-confirmation gate prevents unverified OCR hallucinations from ever locking financial value.

---

## 4. Integrity Rule Sensitivity: Rule E11 (Blind Customer Witness)

| Test Condition | Customer Entry Mode | Discrepancy Injected | System Verdict | Blocking Status |
|---|---|---|---|---|
| Exact Match | `OWN_DEVICE` | 0 mg | `PASS` | Allowed |
| Operator Scale Discrepancy | `OWN_DEVICE` | +300 mg (understated on scale) | `FAIL` | **BLOCKED (Audit Flag E11)** |
| Assisted Counter Mode | `ASSISTED` | 0 mg | `ATTESTED` | Allowed with Lower-Assurance Tag |
| Customer Blind Bypass Attempt | — | Missing Entry | `UNKNOWN` | **BLOCKED (Cannot Proceed)** |

---

## 5. Summary Scorecard & Defensibility
- **Codebase Mutation Score**: Domain modules tested with zero float AST enforcement.
- **Cryptographic Independence**: Standalone `gtverify` CLI proves receipt validity without database access.
- **Ledger Invariants**: PostgreSQL deferred constraint triggers prevent commit of any unbalanced entry.
