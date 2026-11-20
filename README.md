<div align="center">

# 🏆 GOLD TRUST AI

### A Two-Party Evidence, Valuation & Trust Platform for India's Jewellery Ecosystem

[![Tech4Bharat](https://img.shields.io/badge/Hackathon-Tech4Bharat_GAV_Summit-orange?style=for-the-badge)](https://tech4bharat.org)
[![Theme](https://img.shields.io/badge/Theme-Jeweltech_|_Applied_AI-gold?style=for-the-badge)]()
[![PS](https://img.shields.io/badge/Problem_Statement-PS_2.1-blue?style=for-the-badge)]()
[![Status](https://img.shields.io/badge/Status-MVP_In_Progress-brightgreen?style=for-the-badge)]()

---

*Gold Trust AI does not ask customers to trust an AI verdict.*  
*It gives customers and jewellers the same evidence, the same calculation,*  
*the same approved receipt — and a record they can verify later.*

---

</div>

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [Core Engines](#-core-engines)
- [How AI Is Used — Honestly](#-how-ai-is-used--honestly)
- [Consumer Features](#-consumer-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Product Principles](#-product-principles)
- [What Makes This Different](#-what-makes-this-different)
- [Business Model](#-business-model)
- [Project Status](#-project-status)
- [Getting Started](#-getting-started)
- [Team](#-team)

---

## 📖 About the Project

**Gold Trust AI** is a transaction evidence and integrity platform built for India's jewellery ecosystem. It addresses the trust gap that exists on both sides of a gold transaction — the customer who cannot verify how the final amount was calculated, and the jeweller who cannot prove the process was fair and traceable.

The platform captures instrument readings, bill data, and hallmark (HUID) records, validates them for cross-evidence consistency using deterministic rules, computes transparent valuations using integer arithmetic, and produces a single co-signed receipt that both parties can independently verify.

> **Hackathon:** Tech4Bharat — GAV Summit Grand Finale, December 2026, Bangalore Palace  
> **Problem Statement:** PS 2.1 — Gold Purity Verification  
> **Theme:** Jeweltech — Applied AI Systems  
> **Team Size:** 4 Members  
> **Build Horizon:** 6 Weeks

---

## 🔍 The Problem

Gold is one of the most significant household assets in India:

| Metric | Value |
|--------|-------|
| Household gold reserves | 25,000 – 34,600 tonnes |
| Estimated value | $3.8 – 5 trillion |
| Women's share of private gold | ~80 – 85% |
| Rural India's share of annual gold demand | ~55 – 60% |

For many families, a single gold transaction represents months of savings. Yet most jewellery transactions remain **opaque** to the customer.

### Customer-Side Problem

When someone buys a gold necklace or exchanges an old bangle, they typically see a weight, a purity label like "22K," a gold rate, a making charge or deduction, and a final amount. But they **cannot independently verify:**

- Whether the weight on the bill matches what was actually measured on the scale.
- Whether the declared purity is consistent with the hallmark record (HUID).
- What gold rate was applied and whether it reflects the market rate for the day.
- How the making charge or deduction compares to what other shops charge.
- Whether the receipt can be trusted later — for insurance, resale, or a gold loan.

### Jeweller-Side Problem

Honest small jewellers face a parallel documentation gap. Their instrument readings, rate references, deduction policies, customer approvals, and stock movements are spread across paper registers, billing software, and verbal explanations. When a customer disputes a transaction or a regulatory check occurs, the jeweller has **no structured way to prove the process was fair and traceable.**

---

## 💡 Our Solution

Gold Trust AI is **not** a gold-testing device, **not** a photo-based purity classifier, and **not** a simple billing app.

It is an **evidence and transaction integrity platform** that follows an evidence-first workflow:

```
Capture → Validate → Calculate → Explain → Co-sign → Settle → Reconcile → Share / Verify
```

The platform starts with a focused MVP workflow: **old-gold exchange at a participating jeweller's counter** — which brings together weight, purity evidence, rate, deductions, customer approval, settlement, and inventory movement in one transaction.

---

## ⚙️ Core Engines

The system is powered by five interconnected engines:

### 1. Evidence Intake Engine
Captures bill data (via AI-powered OCR), HUID/hallmark details, instrument readings, scale weight, timestamps, and custody photographs. Every piece of evidence is tagged with its **source, operator, and limitations.**

### 2. Cross-Evidence Consistency Engine
Checks whether the bill, hallmark record, instrument reading, and weight agree with each other within defined rules and tolerances. Reports mismatches honestly — **does not guess purity from a photograph** or combine weak signals into a fake confidence score.

### 3. Deterministic Valuation Engine
Calculates fine-gold quantity and settlement amount using **integer arithmetic** (weights in milligrams, purity in permille, money in paise). Every number is reproducible and traceable to a specific rate, deduction policy, and rounding rule.

### 4. Two-Ledger Accounting Engine
Maintains a **separate fine-gold inventory ledger** (in micrograms) and a **financial ledger** (in paise), linked by transaction ID. The jeweller's gold stock and cash records reconcile independently — gold grams and rupees are never mixed in a single accounting unit.

### 5. Shared Receipt & Verification Engine
Produces one **canonical transaction record**, hashed with SHA-256, co-signed by both customer and jeweller. Neither party can silently edit the record after locking. A **QR-based public verification page** allows integrity checks without exposing the customer's personal information.

---

## 🤖 How AI Is Used — Honestly

AI in Gold Trust AI serves **three bounded, well-defined roles:**

| AI Component | Input | Output | Guardrail |
|-------------|-------|--------|-----------|
| **Bill OCR** | Invoice photo / PDF | Extracted fields (weight, purity, rate, GST, deduction) | Human confirmation required for all critical fields |
| **Display Reader** | Scale / instrument display photo | Candidate digits with confidence | Low-confidence readings flagged for manual entry |
| **Receipt Explainer** | Locked receipt JSON + approved templates | Plain-language explanation of receipt lines | Uses only receipt data and approved content |

### What AI Does NOT Do

- ❌ Determine gold purity from a photograph, colour, or video
- ❌ Set market prices or produce uncalibrated trust scores
- ❌ Certify purity or replace BIS hallmarking
- ❌ Claim that multiple weak signals create laboratory-grade certainty
- ❌ Make legal determinations or guarantee compensation

> We believe this honest boundary is a strength, not a limitation — it means every output is **verifiable and defensible.**

---

## 👤 Consumer Features

All consumer features are generated from the same underlying evidence record — they do not upgrade the record into a certified appraisal.

### 🪪 Gold Passport
A portable digital record for each gold item, clearly distinguishing:
- What was **declared** (bill / seller statement)
- What was **measured** (instrument / scale reading)
- What was **verified** against an external source (HUID lookup)
- What **remains unestablished**

### 🛡️ Consumer Rights Card
Educational information about hallmarking requirements, how to check a HUID using official routes, and complaint channels including:
- **BIS Helpline:** 14100
- **National Consumer Helpline:** 1915
- **BIS Care App** for HUID verification

### 🤝 Second Opinion
The customer can share a scoped, expiring evidence summary with another participating jeweller, who reviews it independently and records their agreement or disagreement — **without altering the original assessment.** The original record remains unchanged; the second opinion is appended as a separate event.

### 📋 Gold Loan Readiness Pack
A portable evidence summary the customer can carry to a lender. It clearly states it is **not a certified appraisal** — but gives the lender structured information instead of a loose collection of paper bills.

---

## 🏗️ System Architecture

```
                    CUSTOMER PWA
                         |
                         |
  COUNTER APP ───── API / AUTH / RBAC ───── BACK-OFFICE
                         |
          +--------------+--------------+
          |              |              |
     Evidence       Policy         Customer
     Service        Service        Consent
          |              |              |
          +--------------+--------------+
                         |
                CONSISTENCY ENGINE
                         |
                 VALUATION ENGINE
                         |
             +-----------+-----------+
             |                       |
       GOLD LEDGER             MONEY LEDGER
             |                       |
             +-----------+-----------+
                         |
                RECEIPT / AUDIT
                         |
          +--------------+--------------+
          |              |              |
      QR Verify    Gold Passport   Share / Dispute
                                        |
                                 Second Opinion /
                                 Loan Readiness
```

**Design Decisions:**
- **Modular monolith** — one deployable backend with clear internal boundaries (not microservices)
- **SQLite for prototype** — zero-config, reliable local demo (PostgreSQL migration path ready)
- **No Kafka, Redis, or Kubernetes** — eliminated unnecessary complexity for the MVP

---

## 🛠️ Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | Python + FastAPI | Typed APIs, rapid development, automatic OpenAPI docs |
| **Database** | SQLite (demo) → PostgreSQL (production path) | Zero-config local setup, adequate for single-shop prototype |
| **ORM** | SQLAlchemy | Explicit data models and migration strategy |
| **Frontend** | React + Vite | Fast development cycle and modern UI |
| **Styling** | Tailwind CSS | Consistent, responsive interface |
| **OCR** | Tesseract (local) / Google Vision API (optional) | Bill and display text extraction without external dependency |
| **Image Processing** | OpenCV | Crop, deskew, contrast, display-region preprocessing |
| **PDF Generation** | ReportLab / browser print | Gold Passport and Loan Readiness Pack export |
| **QR Codes** | Python QR library | Share and verification workflows |
| **Testing** | Pytest + property-based tests | Money calculation, state machine, and ledger correctness |
| **Deployment** | Single laptop / local network | Reliable hackathon demonstration |

---

## 📐 Product Principles

These are non-negotiable invariants that guide every design and implementation decision:

| # | Principle | Implementation Consequence |
|---|-----------|---------------------------|
| **P1** | Purity is never inferred from a photograph | Photos document custody and markings — they are not purity evidence |
| **P2** | Every material number has provenance | Source type, source ID, timestamp, operator, and unit are always stored |
| **P3** | AI cannot decide price or purity | AI extracts and explains; deterministic code validates and calculates |
| **P4** | Unknown is a valid result | Missing evidence produces `UNKNOWN`, not a guessed value |
| **P5** | Conflicting evidence is visible | Conflicts block instant settlement and route to review or assay |
| **P6** | No silent edits after lock | Changes require a linked amendment with both-party approval |
| **P7** | Both parties approve the same version | One canonical record hash is shown to customer and jeweller |
| **P8** | Gold and money are separate accounting dimensions | Separate fine-gold and financial ledgers, never mixed |
| **P9** | Privacy by default | Public verification reveals no customer identity or household holdings |
| **P10** | Demo data cannot masquerade as real | Synthetic data has persistent demo labels and a separate database |

---

## 🏅 What Makes This Different

| Existing Category | Typical Focus | Gold Trust AI Differentiation |
|-------------------|--------------|-------------------------------|
| Jewellery ERP / Billing | Billing, inventory, accounting | Customer-visible evidence provenance and co-approved transaction record |
| Hallmark Verification (BIS Care App) | HUID / hallmark record lookup | Joins hallmark data with bill, weight, instrument evidence, and valuation |
| XRF / Testing Equipment | Material measurement | Makes readings, limitations, and transaction arithmetic visible to both parties |
| Consumer Vault / Locker | Document storage | Connects item evidence to a transaction and jeweller stock movement |
| Gold Loan Appraisal | Lender-side valuation | Gives customer a reusable pre-appraisal evidence packet |

**The defensible differentiation:** the *combination* of evidence provenance, cross-source consistency, deterministic valuation, authenticated two-party approval, separate gold/money ledgers, and customer-controlled reuse of the same transaction record — demonstrated in one working platform.

---

## 💼 Business Model

| Customer | Value Delivered | Revenue Model |
|----------|----------------|---------------|
| **Small Jeweller** | Faster documentation, fewer disputes, stock reconciliation, trust differentiation | Shop subscription |
| **Customer** | Portable records, transparent explanation, shareable evidence | Free (core receipt + Gold Passport) |
| **Customer (optional)** | Gold Loan Readiness Pack export | Paid export |
| **Lender (future)** | Structured evidence packet via API | Service contract (to be validated with real users) |

---

## 📊 Project Status

| Component | Status |
|-----------|--------|
| Solution Blueprint & Specification | ✅ Complete |
| Evidence Intake Engine | 🔄 In Progress |
| Cross-Evidence Consistency Engine | 🔄 In Progress |
| Deterministic Valuation Engine | 🔄 In Progress |
| Two-Ledger Accounting | 🔄 In Progress |
| Shared Receipt & Verification | 🔄 In Progress |
| Consumer Features (Passport, Rights Card, Second Opinion, Loan Pack) | 🔄 In Progress |
| Frontend UI (Counter App + Customer PWA) | 🔄 In Progress |
| Demo Scenarios & Testing | ⏳ Planned |

> 🚧 **MVP is approximately 90% complete.** Core engines are functional. Final integration and demo polish are in progress.

---

## 🚀 Getting Started

> *Setup instructions will be updated once the codebase is finalized.*

```bash
# Clone the repository
git clone https://github.com/Karthikdebuger/Tech4bharat.git
cd Tech4bharat

# Backend setup (instructions coming soon)
# Frontend setup (instructions coming soon)
```

---

## 👥 Team

Built by a team of 4 for the **Tech4Bharat Hackathon — GAV Summit Grand Finale**, December 2026, Bangalore Palace.

---

## 📄 License

This project is developed for the Tech4Bharat hackathon. License details to be updated.

---

<div align="center">

---

**Gold Trust AI** does not certify purity. It makes the evidence, the calculation,  
and the uncertainty visible — so both the customer and the jeweller  
can trust the transaction.

---

*Built with purpose for India's jewellery ecosystem* 🇮🇳

</div>
