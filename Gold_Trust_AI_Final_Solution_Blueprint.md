# GOLD TRUST AI

## A Two-Party Evidence, Valuation and Trust Platform for India's Jewellery Ecosystem

**Solution blueprint \| Jeweltech / Applied AI Systems**

**Version:** 1.0 --- Consolidated Hybrid Architecture\
**Status:** Proposed hackathon MVP specification\
**Build horizon:** 6 weeks\
**Team:** 4 people\
**Primary users:** Jewellery customers, independent jewellers and shop
staff

> **Positioning statement:** Gold Trust AI makes a jewellery transaction
> understandable, evidence-backed and verifiable by both the customer
> and the jeweller. It combines instrument readings, hallmark records,
> bill data, transparent valuation rules and a fine-gold inventory
> ledger into one shared transaction record. AI assists with document
> and display reading; deterministic rules control valuation and
> accounting. It does not certify purity, replace BIS hallmarking, or
> replace an assay laboratory.

------------------------------------------------------------------------

# 0. Executive summary

Gold is both a high-value purchase and an important household asset in
India. Yet many jewellery transactions remain difficult for customers to
independently understand. A customer may see a weight, purity label,
gold rate, making charge, deduction or exchange value without being able
to trace how the final amount was calculated. Small jewellers also face
a documentation problem: their readings, rates, deductions, stock
movements and customer approvals may be spread across paper registers,
billing software, photographs and verbal explanations.

Gold Trust AI addresses this two-sided trust gap.

It is not simply a gold-photo classifier, a billing application or a
digital locker. It is a transaction evidence and reconciliation platform
with two connected sides:

1.  **Customer trust:** a clear, itemised explanation of what was
    measured, what was declared, what was calculated, what remains
    uncertain and what the customer approved.
2.  **Jeweller trust:** a reproducible valuation record, published
    deduction policy, authenticated customer approval, traceable stock
    movements and daily reconciliation.

The platform starts with an evidence-first transaction workflow:

**Capture → Validate → Calculate → Explain → Co-sign → Settle →
Reconcile → Share / Verify**

The system has five core engines:

-   **Evidence Intake Engine:** captures bill data, HUID details, scale
    readings, instrument readings, timestamps and custody evidence.
-   **Cross-Evidence Consistency Engine:** checks whether independently
    sourced values agree within defined rules and tolerances. It reports
    mismatches; it does not infer purity from photographs.
-   **Deterministic Valuation Engine:** calculates fine-gold quantity
    and settlement using integer arithmetic, explicit rate basis,
    published deductions and controlled rounding.
-   **Two-Ledger Accounting Engine:** maintains a fine-gold inventory
    ledger and a separate financial ledger, linked by a transaction ID.
-   **Shared Receipt and Verification Engine:** produces one canonical
    transaction record, authenticated approvals, a tamper-evident audit
    trail and a privacy-minimised verification page.

Consumer-facing extensions include a Gold Passport, Consumer Rights
Card, Second Opinion request and Gold Loan Readiness Pack. These are
generated from the underlying evidence record; they do not upgrade the
record into a certified appraisal.

## 0.1 The central promise

For every supported transaction, Gold Trust AI answers five questions:

1.  **What evidence was captured?**
2.  **Which values came from an instrument, hallmark record, bill, rate
    source or shop policy?**
3.  **How was the value calculated?**
4.  **What did both parties approve?**
5.  **Can the record be verified later without exposing unnecessary
    personal data?**

## 0.2 What the product does not claim

Gold Trust AI does not:

-   Determine gold purity from a photograph, colour, video or consumer
    phone camera.
-   Certify purity or replace BIS hallmarking, a recognised assay centre
    or a lender's appraisal.
-   Treat a valid HUID as proof that the present article has not been
    altered after hallmarking.
-   Claim that multiple weak signals automatically create
    laboratory-grade certainty.
-   Set market prices using an LLM.
-   Make legal determinations, guarantee compensation or guarantee loan
    approval.
-   Claim a percentage improvement in accuracy, confidence or processing
    time before measuring it.
-   Claim to be the first or only product of its kind without a
    documented competitor review.

------------------------------------------------------------------------

# 1. Problem definition

## 1.1 The two-sided problem

### Customer-side problem

At purchase, exchange, resale or pledge, customers may struggle to
verify:

-   Whether the item description and declared purity match the available
    hallmark record.
-   Whether the weight shown on the bill is the same weight measured at
    the counter.
-   Whether stones, lac, solder or other non-gold components have been
    accounted for.
-   Which gold-rate basis was used.
-   How making charges, wastage, deductions, taxes or fees affect the
    final amount.
-   Whether the transaction record has changed after the customer left
    the shop.
-   What evidence can be reused when seeking a second opinion or
    approaching a lender.

The customer often has to trust a verbal explanation or a receipt whose
calculations are difficult to reproduce.

### Jeweller-side problem

An honest small jeweller may struggle to prove:

-   Which instrument was used and whether its daily check was completed.
-   Which readings supported the valuation.
-   Which rate snapshot and deduction schedule were applied.
-   Whether the customer saw and accepted the terms.
-   Where old-gold stock moved after intake, melting, refining and
    manufacturing.
-   Whether the HUID register and physical stock reconcile.
-   Whether a later dispute concerns an original reading, a later
    amendment or a different physical article.

A digital record that only stores a final amount does not solve this.
The shop needs a record of the evidence and the stock movement behind
that amount.

## 1.2 Problem statement

**Customers cannot easily verify the evidence and arithmetic behind
jewellery purchases and exchanges, while small jewellers lack a simple,
shared and auditable way to demonstrate how they measured, valued,
documented and accounted for those transactions.**

Gold Trust AI turns the transaction into a shared evidence record and
connects it to transparent valuation and traceable inventory accounting.

## 1.3 Scope of the first release

The first release focuses on one tractable workflow:

**Old-gold exchange at a participating jeweller's counter.**

This is the best MVP workflow because it brings together weight, purity
evidence, rate, deductions, customer approval, settlement and inventory
movement in one transaction.

New-jewellery purchase documentation, Gold Passport management and
loan-readiness exports can be supported as adjacent workflows, but they
must not dilute the core exchange MVP.

------------------------------------------------------------------------

# 2. Product principles and non-negotiable invariants

  -----------------------------------------------------------------------
  ID                      Invariant               Implementation
                                                  consequence
  ----------------------- ----------------------- -----------------------
  P1                      Purity is never         Photos may document
                          inferred from a gold    custody, markings or
                          photograph              instrument displays;
                                                  they are not purity
                                                  evidence

  P2                      Every material number   Store source type,
                          has provenance          source ID, timestamp,
                                                  operator, unit and
                                                  confidence/grade where
                                                  applicable

  P3                      AI cannot decide price  AI extracts or
                          or purity               explains; deterministic
                                                  code validates and
                                                  calculates

  P4                      Unknown is a valid      Missing evidence
                          result                  produces `UNKNOWN`, not
                                                  a guessed value

  P5                      Conflicting evidence is Conflicts block instant
                          visible                 settlement where
                                                  material and route to
                                                  review or assay

  P6                      No silent edits after   Changes require an
                          lock                    amendment linked to the
                                                  original record

  P7                      Both parties approve    One canonical record
                          the same transaction    hash is shown to both
                          version                 parties

  P8                      Integrity is not truth  A hash proves record
                                                  integrity relative to a
                                                  prior hash, not that
                                                  the original
                                                  measurement was correct

  P9                      Gold and money are      Maintain separate
                          separate accounting     fine-gold and financial
                          dimensions              ledgers

  P10                     No unsupported          Report rule outcomes
                          confidence score        and evidence coverage
                                                  unless a calibrated
                                                  model has been
                                                  validated

  P11                     Privacy by default      Public verification
                                                  reveals no customer
                                                  identity or household
                                                  holdings

  P12                     Demo data cannot        Synthetic data has
                          masquerade as real      persistent demo labels
                                                  and a separate
                                                  database/chain

  P13                     Customer choice is      The customer can pause,
                          meaningful              decline, request assay
                                                  or cancel before
                                                  co-signing

  P14                     Policies are versioned  The exact rate,
                                                  deduction schedule and
                                                  calculation version are
                                                  frozen into the receipt
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Users, roles and product surfaces

  -----------------------------------------------------------------------
  Surface                 Primary user            Main purpose
  ----------------------- ----------------------- -----------------------
  Counter application     Jeweller / staff        Capture evidence,
                                                  calculate quote, obtain
                                                  approvals and settle

  Customer PWA            Customer / family       Review quote,
                          member                  understand deductions,
                                                  confirm and retain
                                                  records

  Shop back-office        Owner / manager         Configure policy,
                                                  instruments, stock,
                                                  HUID register and day
                                                  close

  Public verification     Anyone with a receipt   Verify record integrity
  page                    QR                      and selected
                                                  non-personal metadata

  Second Opinion view     Another participating   Review a
                          jeweller                customer-authorised
                                                  evidence packet and
                                                  submit an independent
                                                  opinion

  Loan Readiness export   Customer / lender       Share a limited
                                                  evidence summary;
                                                  lender still performs
                                                  its own appraisal
  -----------------------------------------------------------------------

## 3.1 Roles and permissions

-   **Owner:** shop configuration, staff access, policy publication,
    high-value adjustments and day close.
-   **Manager:** review exceptions, approve permitted amendments and
    reconcile stock.
-   **Counter staff:** create intake, capture readings, generate quotes
    and record settlement within assigned limits.
-   **Customer:** view evidence and quote, approve or decline, receive
    receipt and control sharing.
-   **Second-opinion jeweller:** view only the fields authorised by the
    customer; cannot alter the original assessment.
-   **Public verifier:** check a receipt hash and status; cannot
    retrieve personal or household data.

Role-based access must be enforced by the backend, not only by hiding
buttons in the frontend.

------------------------------------------------------------------------

# 4. End-to-end transaction workflow

## 4.1 Main workflow

``` text
SHOP SETUP
   |
DAILY OPEN
   |-- instrument / scale check
   |-- rate snapshot
   |-- active policy version
   |
CUSTOMER + ITEM INTAKE
   |-- customer consent
   |-- item token and custody photos
   |-- gross weight
   |-- stones / lac / non-gold components
   |
EVIDENCE CAPTURE
   |-- HUID lookup where available
   |-- instrument readings
   |-- display photo and human confirmation
   |-- source and tolerance metadata
   |
CROSS-EVIDENCE VALIDATION
   |-- consistent
   |-- incomplete
   |-- conflict
   |
DETERMINISTIC QUOTE
   |-- fine-gold estimate and range
   |-- rate basis and snapshot
   |-- deductions and reason codes
   |-- taxes / fees where applicable
   |
CUSTOMER + JEWELLER REVIEW
   |-- accept
   |-- request assay / hold
   |-- decline
   |
CO-SIGN + RECEIPT LOCK
   |-- authenticated approvals
   |-- canonical record
   |-- hash and timestamp
   |
SETTLEMENT
   |-- payment evidence
   |-- gold ledger posting
   |-- financial ledger posting
   |
DAY CLOSE
   |-- physical stock reconciliation
   |-- ledger reconciliation
   |-- exception list
   |
SHARE / VERIFY / DISPUTE
```

## 4.2 Transaction state machine

``` text
DRAFT
  |
INTAKE_LOCKED
  |
EVIDENCE_CAPTURED
  |----------------------|
  |                      |
VALIDATION_CLEAR      CONFLICT / INCOMPLETE
  |                      |
QUOTED                REVIEW_REQUIRED
  |                      |
CUSTOMER_REVIEW       ASSAY / ADD_EVIDENCE / CANCEL
  |
COSIGNED
  |
SETTLEMENT_PENDING
  |
SETTLED
  |
CLOSED
```

A dispute can be opened after co-signing. A dispute does not erase or
overwrite the original receipt. It creates a linked case and, if agreed,
a separately signed amendment.

Cancellation is permitted before co-signing and is logged. After
co-signing, reversal is a compensating transaction, not deletion.

## 4.3 Daily open

At the beginning of a shop day:

1.  Staff selects the registered scale and testing instrument.
2.  Staff records the prescribed check-weight / reference sample result.
3.  The system records date, time, operator, expected value, observed
    value and tolerance.
4.  The system captures the shop's declared rate source and rate basis.
5.  The active deduction schedule is frozen for new transactions.
6.  Any missing or failed check creates a visible warning and downgrades
    or disables use according to shop policy.

The MVP should support manual entry with an attached display photo.
Bluetooth integration is not required.

## 4.4 Intake

Capture:

-   Shop transaction ID.
-   Customer-selected name or reference and consent status.
-   Item token ID.
-   Item description and article count.
-   Gross weight in integer milligrams.
-   Stones / lac / non-gold components in integer milligrams, measured
    separately where possible.
-   Scale ID and daily check status.
-   Custody photographs beside a random transaction token card.
-   Staff identity and timestamp.

The photos document which item was handled. They do not establish
purity.

If a non-gold component cannot be separated and weighed reliably, record
the method and uncertainty. Do not silently subtract an estimated
amount.

## 4.5 Evidence capture

Possible sources:

-   HUID record manually checked through an authorised public-facing BIS
    route or other permitted source.
-   XRF or karat-meter reading entered manually or extracted from a
    display photograph.
-   Touchstone estimate recorded as an operator-entered range.
-   Assay report from a recognised centre.
-   Scale display reading.
-   Customer bill or previous receipt.

For each reading store:

-   Source type and source ID.
-   Instrument make/model/serial or shop asset ID.
-   Operator.
-   Timestamp.
-   Reading value and unit.
-   Tolerance and its source.
-   Number and location of sample points, where applicable.
-   Daily check status.
-   Original image/document hash, if attached.
-   AI extraction output and human-confirmation status, if AI was used.

A display-reading model must show the extracted digits and ask a human
to confirm them. Low-confidence or ambiguous digits require manual
entry.

## 4.6 Evidence validation outcomes

The system returns one of:

-   `CONSISTENT`: available sources agree within the configured rules.
-   `INCOMPLETE`: one or more required sources are missing.
-   `CONFLICT`: material disagreement exceeds the defined threshold.
-   `NOT_APPLICABLE`: a source does not apply to this article or
    workflow.
-   `UNVERIFIED`: source could not be independently checked.

These are workflow states, not a universal gold-authenticity score.

------------------------------------------------------------------------

# 5. Evidence model and Cross-Evidence Consistency Engine

## 5.1 Evidence hierarchy

  -----------------------------------------------------------------------
  Evidence type           What it supports        Limit
  ----------------------- ----------------------- -----------------------
  Recognised assay report Tested sample           Scope and sample
                          composition under the   identity still matter
                          report's method         

  Hallmark / HUID record  Registered hallmark     Does not prove the
                          information and marked  present article is
                          purity                  unaltered

  XRF                     Surface composition at  Surface-sensitive; may
                          tested locations        be affected by plating,
                                                  solder, geometry and
                                                  sampling

  Electronic karat meter  Instrument-specific     Depends on device,
                          estimate                calibration and method

  Touchstone              Operator's comparative  Subjective; should be
                          estimate                represented as a range

  Bill                    What the seller         Does not independently
                          declared and charged    prove the article's
                                                  composition

  Scale                   Measured mass under its Depends on calibration,
                          operating conditions    placement and procedure

  Photograph              Visible markings,       Cannot establish gold
                          custody context or      purity
                          instrument display      
  -----------------------------------------------------------------------

Do not collapse all sources into one universal ranking. A bill and a
scale reading answer different questions. The system must preserve the
meaning and limitations of each source.

## 5.2 Core consistency rules

The initial MVP should implement transparent deterministic rules rather
than a trained ensemble.

  -----------------------------------------------------------------------
  Rule ID                 Rule                    Result
  ----------------------- ----------------------- -----------------------
  E01                     HUID format is          Format valid / invalid
                          structurally valid      

  E02                     HUID lookup returns a   Found / not found /
                          record                  unavailable

  E03                     Bill purity label       Match / mismatch /
                          matches the retrieved   unknown
                          hallmark record, where  
                          comparable              

  E04                     Bill weight matches     Match / mismatch /
                          measured weight within  unknown
                          configured tolerance    

  E05                     Instrument readings     Pass / repeat / assay
                          meet the configured     review
                          spread rule             

  E06                     Rate used is within the In band / exception
                          shop's declared         
                          reference band or has   
                          an exception reason     

  E07                     Deduction is within the Pass / exception /
                          active published policy blocked
                          cap                     

  E08                     Daily instrument and    Valid / downgraded /
                          scale checks are        blocked
                          current                 

  E09                     Required customer and   Complete / incomplete
                          jeweller approvals      
                          exist                   

  E10                     Settlement and          Balanced / exception
                          inventory postings      
                          balance                 
  -----------------------------------------------------------------------

The original seven-rule concept can be retained as a product narrative,
but implementation should use a rule catalogue with versioning. Do not
force unrelated checks into exactly seven rules.

## 5.3 Conflict handling

A conflict is raised when:

-   A bill and HUID record materially disagree on a comparable field.
-   Instrument readings differ beyond the instrument-specific spread
    threshold.
-   Two comparable purity sources disagree beyond their combined
    uncertainty.
-   The measured weight does not reconcile with the bill or custody
    stages within configured tolerance.
-   The evidence identity is uncertain (for example, the photo token
    does not match the transaction token).

A conflict must not be converted into a negative accusation. It should
state:

-   Which sources disagree.
-   Their values and provenance.
-   The rule and threshold that triggered the conflict.
-   What the system cannot determine.
-   The next available action: repeat reading, inspect additional
    points, request documentation or use an assay centre.

## 5.4 Sampling protocol

For instruments that support multi-point testing:

1.  Follow the instrument manufacturer's operating procedure.
2.  Use distinct representative locations selected under a documented
    shop protocol.
3.  Record each point, not only the average.
4.  Record instrument tolerance and daily check status.
5.  If the spread exceeds the configured limit, repeat or route to
    assay.
6.  Do not claim that three points guarantee whole-article purity.

The number of points and spread threshold must be configurable by
instrument model and supported by its documentation or a validated
operating procedure. The example of three points is a workflow
parameter, not a universal scientific guarantee.

## 5.5 Why no photo-based purity classifier

A consumer camera captures visible appearance, not elemental
composition. Lighting, white balance, polish, plating, alloy composition
and camera processing can change appearance. A CNN trained on
photographs could learn lighting or background correlations rather than
gold purity.

For that reason, Gold Trust AI uses images only for:

-   Reading instrument and scale displays.
-   Reading printed or handwritten documents, with confidence and human
    review.
-   Recording item custody and visible hallmark markings.
-   Showing the customer which item was tested.

Photo-based purity prediction is out of scope.

------------------------------------------------------------------------

# 6. AI architecture: useful, bounded and testable

## 6.1 AI components

  -----------------------------------------------------------------------
  Component         Input             Output            Guardrail
  ----------------- ----------------- ----------------- -----------------
  Bill OCR          Invoice photo/PDF Candidate fields  Human
                                      and text regions  confirmation for
                                                        critical fields

  Display reader    Scale /           Candidate digits, Never auto-lock a
                    instrument        units and         reading
                    display photo     confidence        

  Receipt explainer Locked receipt    Plain-language    Retrieval only
                    JSON and approved explanation /     from that receipt
                    templates         speech            and approved
                                                        rights content

  Dispute           Signed            Neutral timeline  Cannot decide who
  summariser        transaction       and recomputation is right
                    timeline          summary           

  Optional anomaly  Structured        Review flags      Must be
  triage            transaction                         validated; never
                    features                            changes price or
                                                        purity
  -----------------------------------------------------------------------

## 6.2 Deterministic components

The following must be ordinary, testable application code:

-   Unit conversion.
-   Fine-gold calculation.
-   Rate conversion.
-   Deduction calculation.
-   Final rounding.
-   Tolerance and conflict rules.
-   Policy caps.
-   Ledger posting.
-   Receipt canonicalisation.
-   Hash calculation.
-   Signature verification.
-   Reconciliation.
-   State transitions.

## 6.3 Why an XGBoost model is not in the MVP

The v4 proposal includes XGBoost and SHAP. This is not automatically a
better AI solution.

A supervised model needs a representative labelled dataset with reliable
ground truth. A small team is unlikely to obtain enough diverse,
correctly labelled jewellery transaction cases in six weeks. Synthetic
data can test software behaviour but cannot establish real-world
predictive accuracy.

Therefore:

-   Do not train a model merely to display an AI score.
-   Do not report accuracy on synthetic demo cases as real-world
    performance.
-   If a later model is introduced, define the target label,
    ground-truth process, dataset provenance, train/test separation,
    class balance, calibration and error costs.
-   Use SHAP only after a validated model exists and only to explain
    that model's output.

The MVP's AI depth comes from multimodal document/display extraction and
grounded explanation, combined with a deterministic evidence engine.

## 6.4 Confidence and uncertainty

Do not display a single `Trust Score: 92%` unless it has been
statistically calibrated against an independently labelled dataset.

Instead display:

-   Evidence coverage: `6 of 8 applicable checks completed`.
-   Rule results: `5 pass, 1 mismatch, 2 unavailable`.
-   Evidence grades and source limitations.
-   A clear outcome: `Consistent`, `Incomplete` or `Conflict`.
-   A separate OCR confidence for each extracted field, where the model
    provides it.

OCR confidence is not transaction confidence.

## 6.5 Offline and degraded operation

The core valuation and ledger workflow must work without AI services or
internet access after shop setup.

-   AI unavailable: manual entry.
-   HUID service unavailable: mark `UNVERIFIED / SERVICE UNAVAILABLE`;
    do not mark valid.
-   Rate source unavailable: use only a still-valid, explicitly approved
    shop rate snapshot or pause quoting.
-   Notary service unavailable: store a locally signed pending record
    and clearly label it `NOT YET ANCHORED`; do not claim public
    verification.
-   WhatsApp unavailable: generate a downloadable receipt and QR
    locally.

------------------------------------------------------------------------

# 7. Deterministic valuation engine

## 7.1 Units and conventions

Use integer storage to avoid floating-point drift.

  Quantity     Storage
  ------------ --------------------------------------------
  Weight       Integer milligrams (mg)
  Fine gold    Integer micrograms (µg)
  Purity       Integer permille (‰)
  Rate         Integer paise per fine gram
  Deductions   Integer basis points (bp)
  Money        Integer paise
  Timestamp    UTC internally; local timezone for display

The receipt must state the rate basis explicitly, such as rupees per
gram of fine gold on a declared 1000‰ basis. Do not mix 999 and 1000
conventions without an explicit conversion.

## 7.2 Core formulas

Let:

-   `gross_mg` = gross measured article weight.
-   `stones_mg` = separately measured non-gold components.
-   `other_removed_mg` = other separately measured removed components.
-   `fineness_permille` = selected purity value in ‰.
-   `deduction_bp` = deduction in basis points.
-   `rate_paise_per_g` = declared rate in paise per fine gram.

``` text
net_mg = gross_mg - stones_mg - other_removed_mg

fine_ug = net_mg * fineness_permille

payable_fine_ug = round_policy(
    fine_ug * (10000 - deduction_bp) / 10000
)

value_paise = round_half_up(
    payable_fine_ug * rate_paise_per_g / 1_000_000
)
```

Because `mg × ‰ = µg`, the fine-gold unit conversion is exact under this
representation.

The implementation must use integer/rational arithmetic. The final
currency amount is rounded once under a documented half-up policy. Any
accounting residue is posted to a financial rounding account in paise,
not to the gold inventory ledger.

## 7.3 Tolerance range

For a reading with a justified tolerance:

``` text
low_fineness = max(0, measured_fineness - tolerance)
high_fineness = min(1000, measured_fineness + tolerance)
```

Calculate low, midpoint and high valuation using the same deduction and
rate assumptions. Display the range and state which point is used for
settlement.

A tolerance range is not a statistical confidence interval unless the
instrument documentation and validation support that interpretation.

## 7.4 Rate source

The shop declares:

-   Rate value.
-   Unit and purity basis.
-   Source name.
-   Source timestamp.
-   Capture timestamp.
-   Validity window.
-   Whether the rate is supplier-declared, association-published or
    another reference.
-   Exception reason if outside the configured comparison band.

A public rate reference is a comparison aid, not a universal truth.
Different sources may use different city, purity, tax, retail and timing
conventions. The system must normalise before comparing.

## 7.5 Deduction schedule

Each shop publishes a versioned schedule:

-   Policy code.
-   Article category.
-   Applicability conditions.
-   Deduction basis.
-   Deduction amount or percentage.
-   Maximum cap.
-   Reason shown to customer.
-   Whether the deduction applies before or after another calculation.
-   Effective date.
-   Exception rules.
-   Owner approval.
-   Policy hash.

The system enforces the cap. Any exception requires a reason code and
explicit customer approval. The customer sees the schedule before
co-signing.

The platform does not prescribe a universal "fair" deduction percentage.
Actual practices vary by item, process and shop; collect field data
before proposing benchmarks.

## 7.6 Worked example (illustrative only)

All numbers below are sample parameters for software testing, not market
rates or standard deductions.

  Step                        Illustrative value
  ---------------------- -----------------------
  Gross weight                          31.400 g
  Stones / lac removed                   0.600 g
  Net metal                             30.800 g
  Instrument result                         905‰
  Example tolerance                          ±5‰
  Fine gold midpoint                    27.874 g
  Example rate             ₹13,000 per fine gram
  Example deduction                        2.00%
  Payable fine gold                   27.31652 g
  Calculated value                   ₹355,114.76
  Final rounded amount                  ₹355,115

The software test must verify the exact integer result and the low/high
range. The interface must label all example inputs as illustrative.

## 7.7 Mode A and Mode B

**Mode A --- immediate settlement based on agreed evidence**

-   Uses the selected evidence grade and declared calculation policy.
-   Shows the measured value, tolerance range, deduction and settlement.
-   Is allowed only when no blocking conflict exists.
-   Customer and jeweller approve the same quote.

**Mode B --- hold and verify by assay**

-   The parties agree to hold settlement or make a clearly documented
    advance, if the shop's policy and applicable law permit.
-   Custody of the item is recorded.
-   The melt/button is weighed and the assay report is attached.
-   Final settlement is calculated from the assay result under a
    pre-agreed policy.
-   Assay fee, payer and treatment are shown before consent.

Do not compare Mode A and Mode B using inconsistent deduction rules. The
customer must see whether the same deduction applies in both modes and
why. If policies differ, show the difference explicitly.

------------------------------------------------------------------------

# 8. Accounting: two linked ledgers, not one mixed ledger

This is a critical design decision.

Gold quantity and money are different accounting dimensions. They must
not be mixed in one balancing journal.

## 8.1 Fine-gold inventory ledger

All quantities are stored as integer micrograms or a precisely defined
subunit.

Suggested accounts:

-   `Stock:OldGold`
-   `Stock:Refined`
-   `Stock:WorkInProgress`
-   `Stock:FinishedItems`
-   `Stock:Scrap`
-   `Customer:GoldPayable`
-   `Variance:Melt`
-   `Variance:Process`
-   `Variance:Unexplained`

Every gold journal entry balances in fine-gold units.

Illustrative intake:

  Debit                        Credit
  ---------------------------- -----------------------------------
  `Stock:OldGold` 27.87400 g   `Customer:GoldPayable` 27.31652 g
                               `Retained:Deduction` 0.55748 g

This entry balances in gold quantity.

Illustrative later melt:

  Debit                        Credit
  ---------------------------- ----------------------------
  `Stock:Refined` 27.77045 g   `Stock:OldGold` 27.87400 g
  `Variance:Melt` 0.10355 g    

The example records a difference; it does not automatically classify the
difference as acceptable. The shop's documented process and threshold
determine whether it is an exception.

## 8.2 Financial ledger

Separate financial accounts may include:

-   `Cash`
-   `Bank`
-   `Customer:CashPayable`
-   `Customer:CashReceivable`
-   `AssayExpense`
-   `ServiceFee`
-   `TaxPayable` (only when configured by qualified accounting advice)
-   `RoundingDifference`

All entries balance in integer paise.

For a cash settlement, debit the relevant customer payable and credit
cash/bank according to the actual payment. Do not invent tax treatment.
The MVP records tax fields supplied by the shop; production tax
computation requires professional review.

## 8.3 Link between ledgers

Both journals carry:

-   Exchange ID.
-   Receipt hash.
-   Posting ID.
-   Effective timestamp.
-   Actor.
-   Reversal/amendment reference.

The exchange record links the gold payable quantity and cash settlement
amount. The system must not pretend that gold quantity and money balance
against each other in a single ledger.

## 8.4 Day-close reconciliation

Day close compares:

1.  Opening fine-gold stock.
2.  Intake.
3.  Refining and process movements.
4.  Purchases and sales.
5.  Transfers and returns.
6.  Physical counted stock.
7.  Unexplained variance.

Every tolerance must be configured and justified by the shop's process.
An unexplained difference creates an exception; the system must never
auto-adjust inventory to force a balance.

------------------------------------------------------------------------

# 9. Shared receipt, signatures and tamper evidence

## 9.1 Canonical receipt

After both parties approve the quote, the backend creates one canonical
JSON record containing:

-   Schema version.
-   Exchange ID.
-   Shop ID.
-   Item token IDs.
-   Evidence references and grades.
-   Reading values and units.
-   Rate snapshot.
-   Policy version and hash.
-   Calculation version.
-   Quote lines and totals.
-   Settlement choice.
-   Customer and jeweller approval metadata.
-   Demo/real mode flag.
-   Creation timestamp.

Canonicalisation must be deterministic: stable key ordering, explicit
number/string representation, explicit null handling and a documented
schema version.

## 9.2 Hash

Compute SHA-256 over the canonical byte representation. The hash
identifies that exact record version.

A hash alone does not authenticate the parties, prove the measurement
was correct or prevent a malicious person from creating a new fake
record. It only helps detect a change when compared with a trusted prior
hash.

## 9.3 Authentication and approval

Record two distinct approval events:

-   Customer approval: authenticated session, OTP or assisted PIN flow.
-   Jeweller approval: authenticated staff account and role.

Each approval event includes:

-   Actor identity or pseudonymous ID.
-   Authentication method.
-   Timestamp.
-   Receipt hash being approved.
-   Consent text version.
-   Device/session metadata, minimised appropriately.

For a production-grade design, use cryptographic signatures or a trusted
signing service with managed keys. For the hackathon MVP, authenticated
backend approval events plus immutable audit logging may be implemented,
but the UI must not describe this as a legally qualified digital
signature unless that has been established.

Assisted approval must be visibly labelled as assisted and must not be
presented as equivalent to customer-controlled approval.

## 9.4 Append-only log and public verification

MVP implementation:

-   Store receipt hash and timestamp in an append-only audit table.
-   Prevent normal application roles from updating or deleting log
    entries.
-   Export a daily hash manifest.
-   Generate a daily root or signed manifest.
-   Publish or externally anchor the root only if a real independent
    mechanism is implemented.

Do not call an internal database table a public notary. If the MVP has
no independent timestamping or external anchor, label it accurately as
an application audit log.

## 9.5 Amendments

No post-lock overwrite.

An amendment contains:

-   Original receipt hash.
-   New receipt hash.
-   Field changed.
-   Old and new values.
-   Reason.
-   Requesting actor.
-   Both parties' approval events where the change affects agreed terms.
-   Timestamp.

The verification page displays the chain.

## 9.6 QR verification page

Show only:

-   Receipt hash.
-   Receipt status.
-   Timestamp or anchoring status.
-   Evidence categories and grades.
-   Policy version.
-   Calculation version.
-   Approval status.
-   Amendment status.
-   Demo/real status.

Do not show customer name, phone, address, family gold holdings, full
bill or raw documents on the public page.

------------------------------------------------------------------------

# 10. Customer features

## 10.1 Gold Passport

A customer-controlled record for each item or transaction.

Fields:

-   Customer-defined item nickname.
-   Item description.
-   Purchase or exchange date.
-   Declared purity.
-   Hallmark/HUID details where available.
-   Weight and source of weight.
-   Bill reference and document hash.
-   Transaction evidence summary.
-   Receipt hash.
-   Important limitations.

The Passport must distinguish:

-   **Declared:** what the bill or seller states.
-   **Recorded:** what the instrument or scale measured.
-   **Verified against source:** what an external record returned.
-   **Not established:** what the available evidence cannot prove.

Do not create a single "certified gold value" field.

## 10.2 Consumer Rights Card

The card provides general educational information and official complaint
routes.

It must:

-   Explain how to check a hallmark/HUID using the official BIS route.
-   Explain that applicable hallmarking requirements have exemptions and
    scope conditions.
-   Explain that consumers should retain the bill and test
    documentation.
-   State that remedies depend on applicable rules and the facts of the
    case.
-   Link to current official BIS and National Consumer Helpline
    resources.
-   Avoid guaranteeing a compensation amount or replacement.

Legal content must be reviewed against current official rules before
public release. The app should show the source and last-reviewed date.

## 10.3 Second Opinion

Purpose: allow a customer to request an independent review of the
evidence packet.

Flow:

1.  Customer chooses a receipt or item.
2.  Customer selects which fields/documents to share.
3.  System creates an expiring, revocable token.
4.  Another participating jeweller scans the QR.
5.  The reviewer sees the authorised evidence summary and limitations.
6.  Reviewer records `AGREE`, `PARTIALLY_AGREE`, `DISAGREE` or
    `INSUFFICIENT_EVIDENCE`.
7.  Reviewer provides a reason and may attach their own instrument/assay
    evidence.
8.  Customer receives the review.
9.  Original assessment remains unchanged; the second opinion is
    appended as a separate event.

Do not increase an AI confidence score merely because a reviewer agrees.
The system reports the independent opinion and its evidence.

Controls:

-   Reviewer identity and shop credentials are displayed.
-   Conflict-of-interest declaration.
-   No access to unrelated customer items.
-   Token expiry and revocation.
-   Rate limiting and abuse reporting.
-   No paid ranking that disguises commercial promotion as neutral
    verification.

## 10.4 Gold Loan Readiness Pack

A portable evidence summary that helps a customer prepare for a lender's
appraisal.

Include:

-   Item description.
-   Declared and recorded weight, with source.
-   Hallmark/HUID lookup status and timestamp.
-   Available instrument/assay evidence and grade.
-   Receipt hash and verification link.
-   Outstanding conflicts or missing evidence.
-   Date and expiry of the share link.
-   Explicit statement: **not a certified appraisal, loan sanction,
    purity guarantee or lender valuation**.

Do not label an AI estimate as "pre-verified gold value." Lenders
perform their own appraisal, eligibility checks and valuation.

For the MVP, generate a PDF and a privacy-scoped verification URL. A
real lender API integration is out of scope unless a formal partner and
API specification exist.

## 10.5 Receipt explainer

The customer can select a receipt line and request a plain-language
explanation.

Example:

-   "Net metal weight" means the gross weight after separately measured
    stones and other removed components are subtracted.
-   "Fine gold" is the calculated gold content based on the selected
    fineness reading.
-   "Deduction" is the shop's published deduction under the policy shown
    on this receipt.
-   "Range" reflects the stated instrument tolerance; it is not a
    guarantee of the final assay result.

The explainer must use the receipt JSON and approved content. It must
not answer unsupported questions about purity or legal rights.

------------------------------------------------------------------------

# 11. Jeweller features

## 11.1 Counter workflow

The counter app should make the correct workflow the easiest workflow:

1.  Start exchange.
2.  Capture item and weight.
3.  Record removed components.
4.  Add HUID and instrument evidence.
5.  Review consistency result.
6.  Generate itemised quote.
7.  Show customer the same quote.
8.  Obtain both approvals.
9.  Record settlement.
10. Update stock and financial ledgers.

Target a short workflow, but do not claim a specific time saving until
measured with real shopkeepers.

## 11.2 Published shop policy

The shop can publish:

-   Rate source and basis.
-   Deduction schedule.
-   Assay fee policy.
-   Rate-lock duration.
-   Exception rules.
-   Settlement modes.
-   Customer complaint contact.

Every quote references the exact policy version. The customer can view
the current schedule and prior versions.

## 11.3 HUID register

Record:

-   HUID.
-   Article type.
-   Declared/marked purity.
-   Source and lookup timestamp.
-   Article status as returned by the source.
-   Related transaction ID.
-   Sale/return/repair status entered by the shop.
-   Exceptions such as duplicate or missing records.

Do not assume a future BIS "sold" status feature or an undocumented
public API. Use only currently available, permitted lookup mechanisms.
If no API is available, support manual lookup and evidence attachment.

## 11.4 Day-close dashboard

Show:

-   Opening stock.
-   Old-gold intake.
-   Refined gold.
-   Work in progress.
-   Finished items.
-   Sales and transfers.
-   Melt/process variance.
-   Physical count.
-   Unexplained variance.
-   Missing HUID records.
-   Unsettled transactions.
-   Instrument checks missing or failed.
-   Policy exceptions.
-   Amendments and disputes.

The dashboard is an exception-management tool, not a mechanism to
automatically conceal or repair discrepancies.

------------------------------------------------------------------------

# 12. Hardware strategy

## 12.1 Principle

**Software is the complete MVP. Hardware is an optional evidence
adapter.**

A phone-only workflow is valid when staff manually enter readings from a
shop's existing calibrated instrument and attach the display evidence.
It is not equivalent to an independent purity test.

## 12.2 Optional hardware

Potential components:

-   Load cell and HX711 for weight measurement.
-   ESP32-S3 for local communication.
-   A supported display or serial interface from an existing instrument,
    where permitted.

An AS7341 or similar spectral sensor may be explored for research, but
it must not be described as a gold purity analyser without controlled
validation against laboratory measurements.

## 12.3 Hardware claims

Do not claim:

-   A particular accuracy improvement without validation.
-   That a low-cost sensor replaces a calibrated jewellery scale.
-   That a spectral response establishes karatage.
-   That sensor data is tamper-proof merely because it comes from a
    microcontroller.

If hardware is built, capture calibration data, reference weights,
repeatability, drift and comparison against a traceable reference. Keep
it out of the critical path for the hackathon MVP.

------------------------------------------------------------------------

# 13. System architecture

## 13.1 Logical architecture

``` text
                 CUSTOMER PWA
                      |
                      |
COUNTER APP ---- API / AUTH / RBAC ---- BACK-OFFICE
                      |
      +---------------+----------------+
      |               |                |
 Evidence Service  Policy Service   Customer Consent
      |               |                |
      +---------------+----------------+
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
       +--------------+----------------+
       |              |                |
   QR Verify     Gold Passport    Share / Dispute
                                      |
                              Second Opinion /
                              Loan Readiness
```

## 13.2 Recommended six-week stack

  -----------------------------------------------------------------------
  Layer                   Technology              Reason
  ----------------------- ----------------------- -----------------------
  Backend                 Python + FastAPI        Typed APIs, rapid
                                                  development, automatic
                                                  docs

  Database                SQLite for demo;        Simple local setup;
                          PostgreSQL migration    adequate for
                          path                    single-shop prototype

  ORM                     SQLAlchemy              Explicit data models
                                                  and migration path

  Frontend                React + Vite            Fast UI development

  Styling                 Tailwind CSS            Consistent responsive
                                                  interface

  OCR                     Tesseract initially;    Avoid external service
                          optional managed OCR    dependency in core flow

  Image handling          OpenCV                  Crop, deskew, contrast
                                                  and display-region
                                                  preprocessing

  AI explanation          LLM with constrained    Language support and
                          receipt context,        explanation, not
                          optional                decision-making

  PDF                     ReportLab or browser    Passport and
                          print                   loan-readiness export

  QR                      Python QR library       Share and verify
                                                  workflows

  Testing                 Pytest + property-based Money, state and ledger
                          tests                   correctness

  Deployment              One laptop / local      Reliable hackathon
                          network                 demonstration
  -----------------------------------------------------------------------

Avoid Kafka, Kubernetes, Redis, microservices and multiple databases in
the six-week MVP. They add operational complexity without improving the
core proof.

## 13.3 Backend module structure

``` text
backend/
  app/
    main.py
    api/
      auth.py
      exchanges.py
      evidence.py
      quotes.py
      receipts.py
      ledger.py
      shares.py
      disputes.py
      second_opinion.py
      passport.py
    core/
      config.py
      security.py
      permissions.py
      canonical_json.py
      hashing.py
    domain/
      evidence_rules.py
      valuation.py
      gold_ledger.py
      money_ledger.py
      reconciliation.py
      state_machine.py
    models/
      shop.py
      staff.py
      customer.py
      instrument.py
      policy.py
      exchange.py
      reading.py
      receipt.py
      ledger.py
      consent.py
      share.py
      dispute.py
    services/
      ocr.py
      display_reader.py
      huid_adapter.py
      rate_adapter.py
      pdf_export.py
      notification.py
    tests/
      test_valuation.py
      test_rounding.py
      test_evidence_rules.py
      test_state_machine.py
      test_ledgers.py
      test_permissions.py
      test_receipt_integrity.py
```

This is a modular monolith: one deployable backend with clear internal
boundaries.

------------------------------------------------------------------------

# 14. Data model

Core entities:

  -----------------------------------------------------------------------
  Entity                              Important fields
  ----------------------------------- -----------------------------------
  Shop                                id, name, location, settings,
                                      active_policy_id

  Staff                               id, shop_id, role, auth status

  Customer                            id, optional contact reference,
                                      consent status

  Instrument                          id, shop_id, type, make/model,
                                      serial, tolerance source

  CheckLog                            instrument_id, date, expected,
                                      observed, result, operator

  PolicyVersion                       shop_id, version, schedule JSON,
                                      hash, effective date

  RateSnapshot                        value, currency, unit, purity
                                      basis, source, timestamp

  Exchange                            id, shop_id, customer_id, state,
                                      created_at

  Item                                id, exchange_id, description, token

  Evidence                            id, exchange_id, type, source,
                                      grade, payload, file hash

  Reading                             evidence_id, value, unit,
                                      tolerance, point index

  ValidationResult                    exchange_id, rule version, outcome,
                                      explanation

  Quote                               exchange_id, calculation version,
                                      line items, totals

  Approval                            receipt hash, actor, method,
                                      consent version, timestamp

  Receipt                             canonical JSON, hash, status,
                                      schema version

  Amendment                           original hash, new hash, changed
                                      fields, reason

  GoldJournal                         transaction id, account, debit µg,
                                      credit µg

  MoneyJournal                        transaction id, account, debit
                                      paise, credit paise

  HUIDRecord                          HUID, source response, lookup
                                      timestamp, status

  Consent                             customer, purpose, scope, timestamp

  Share                               token hash, fields, expiry,
                                      revocation status

  SecondOpinion                       share id, reviewer, opinion,
                                      reason, evidence

  Dispute                             exchange id, opened_by, timeline,
                                      resolution

  AuditEvent                          actor, action, object, timestamp,
                                      previous hash
  -----------------------------------------------------------------------

Store uploaded documents in a controlled file store. Store their content
hashes and access permissions in the database. Do not put raw customer
documents on the public verification endpoint.

------------------------------------------------------------------------

# 15. API design

Example endpoint contract:

  --------------------------------------------------------------------------------------
  Method                  Endpoint                               Purpose
  ----------------------- -------------------------------------- -----------------------
  POST                    `/api/v1/exchanges`                    Create exchange

  POST                    `/api/v1/exchanges/{id}/items`         Add item

  POST                    `/api/v1/exchanges/{id}/evidence`      Attach evidence

  POST                    `/api/v1/exchanges/{id}/readings`      Record instrument/scale
                                                                 readings

  POST                    `/api/v1/exchanges/{id}/validate`      Run consistency rules

  POST                    `/api/v1/exchanges/{id}/quote`         Calculate deterministic
                                                                 quote

  POST                    `/api/v1/exchanges/{id}/approvals`     Record
                                                                 customer/jeweller
                                                                 approval

  POST                    `/api/v1/exchanges/{id}/settle`        Record settlement and
                                                                 post journals

  GET                     `/api/v1/receipts/{hash}`              Retrieve authorised
                                                                 receipt

  GET                     `/api/v1/verify/{hash}`                Public
                                                                 privacy-minimised
                                                                 verification

  POST                    `/api/v1/receipts/{hash}/amendments`   Propose amendment

  GET                     `/api/v1/ledger/gold/daily`            Gold stock day close

  GET                     `/api/v1/ledger/money/daily`           Financial day close

  POST                    `/api/v1/shares`                       Create scoped share

  POST                    `/api/v1/shares/{token}/revoke`        Revoke share

  GET                     `/api/v1/second-opinion/{token}`       Reviewer view

  POST                    `/api/v1/second-opinion/{token}`       Submit independent
                                                                 opinion

  POST                    `/api/v1/disputes`                     Open dispute

  GET                     `/api/v1/passports/{id}`               Customer Passport

  POST                    `/api/v1/loan-readiness/{item_id}`     Generate evidence pack
  --------------------------------------------------------------------------------------

Every endpoint must enforce authentication, shop-level tenant isolation,
role permissions, consent and state-machine rules.

------------------------------------------------------------------------

# 16. Security, privacy and misuse controls

## 16.1 Threat model

  -----------------------------------------------------------------------
  Threat                              Control
  ----------------------------------- -----------------------------------
  Jeweller edits reading after seeing Lock evidence; amendments are
  customer response                   linked and visible

  Customer denies approved terms      Authenticated approval event tied
                                      to receipt hash

  Staff fabricates reading            Instrument/operator provenance,
                                      check logs, custody evidence,
                                      random audit

  Customer submits forged receipt     Verify hash and approval/audit
                                      chain

  Staff accesses another shop's       Tenant isolation and server-side
  records                             access control

  Public QR leaks identity            Public endpoint returns minimal
                                      fields only

  Share link forwarded                Short expiry, revocation, field
                                      scope, access log

  Demo data appears real              Separate demo store, permanent
                                      watermark and demo QR domain/path

  API key leaked                      Environment secrets, no secrets in
                                      frontend, rotation

  Database tampering                  Restricted write access, audit log,
                                      backups and external root anchoring
                                      where available
  -----------------------------------------------------------------------

## 16.2 Privacy model

-   Collect only information needed for the transaction.
-   Do not create a central family gold-holdings dashboard.
-   Do not expose customer lists across shops.
-   Keep customer vault data separate from public verification data.
-   Use per-item shares with selected fields, expiry and revocation.
-   Log who viewed a share.
-   Encrypt sensitive data in transit and at rest where the deployment
    supports it.
-   Provide export and deletion workflows subject to legal
    record-retention obligations.
-   Obtain consent for each sharing purpose.

Legal compliance under India's data protection framework must be checked
against the provisions and rules in force at deployment. Do not claim
compliance solely because a consent checkbox exists.

## 16.3 Misuse symmetry

The system must protect both sides:

-   A jeweller cannot silently change the evidence or deduction.
-   A customer cannot silently rewrite the receipt after settlement.
-   Neither party can backdate an existing locked receipt without a
    visible amendment.
-   Neither party can use a public QR to access private data.
-   Neither party can force a second-opinion result to overwrite the
    original record.

------------------------------------------------------------------------

# 17. Business model and adoption

## 17.1 Who pays and why

  -----------------------------------------------------------------------
  Customer                Value delivered         Possible model
  ----------------------- ----------------------- -----------------------
  Small jeweller          Faster documentation,   Shop subscription
                          fewer disputes, stock   
                          reconciliation and      
                          trust differentiation   

  Customer                Portable records,       Free core receipt;
                          explanation and         optional paid export
                          shareable evidence      only if validated

  Lender                  Structured evidence     Future API/service
                          packet                  contract

  Assay centre            Better-organised        Referral/workflow
                          customer intake and     partnership, subject to
                          report linkage          independence safeguards
  -----------------------------------------------------------------------

Do not assume lenders will pay per verification or that consumers will
pay a particular price without interviews and pilots.

## 17.2 Adoption wedge

Start with 3--5 local jewellers and one workflow. Do not begin by trying
to onboard an entire national jewellery network.

The first adoption test is:

**Will a jeweller use the counter workflow repeatedly because it saves
effort, reduces disputes or improves customer confidence?**

Measure:

-   Time to complete intake and quote.
-   Staff training time.
-   Number of fields requiring manual correction.
-   Customer understanding of deductions.
-   Frequency of disputes and repeat explanations.
-   Daily reconciliation completion.
-   Willingness to pay after a real pilot.

## 17.3 Network effects

Second Opinion can create a network, but only if independent reviewers
are trusted and customers can compare opinions without coercion.

Do not sell a "verified jeweller" badge based solely on subscription
payment. Define transparent verification criteria, evidence of
credentials and a complaints process.

------------------------------------------------------------------------

# 18. Competitor and differentiation strategy

Do not claim "no competitor does this" without a documented competitor
sweep.

Compare categories rather than making unsupported claims about named
products:

  -----------------------------------------------------------------------
  Existing category       Typical focus           Gold Trust AI
                                                  differentiation to test
  ----------------------- ----------------------- -----------------------
  Jewellery ERP / billing Billing, inventory and  Customer-visible
                          accounting              evidence provenance and
                                                  co-approved transaction
                                                  record

  Hallmark verification   HUID/hallmark record    Joins hallmark data
                          lookup                  with bill, weight,
                                                  instrument evidence and
                                                  valuation

  XRF / testing equipment Material measurement    Makes readings,
                                                  limitations and
                                                  transaction arithmetic
                                                  visible to both parties

  Consumer vault / locker Document storage        Connects item evidence
                                                  to a transaction and
                                                  jeweller stock movement

  Gold loan appraisal     Lender-side valuation   Gives customer a
                                                  reusable pre-appraisal
                                                  evidence packet without
                                                  replacing lender
                                                  appraisal
  -----------------------------------------------------------------------

Before claiming differentiation, research at least 5--8 products used by
jewellers and consumers. Record product name, geography, customer,
supported workflow, integrations, pricing if public, and gap. A
competitor may already offer part of the proposed workflow.

**Defensible differentiation:** the combination of evidence provenance,
deterministic transaction valuation, dual approval, linked
gold/financial ledgers and customer-controlled reuse of the record. The
combination must be demonstrated, not merely asserted.

------------------------------------------------------------------------

# 19. Six-week build plan for four people

## 19.1 Team roles

  -----------------------------------------------------------------------
  Person                  Primary ownership       Backup
  ----------------------- ----------------------- -----------------------
  P1                      Backend, data model,    Security and
                          valuation and ledgers   integration

  P2                      React UI, counter flow, Demo integration
                          customer PWA and        
                          accessibility           

  P3                      OCR, display reading,   Backend evidence API
                          evidence rules and test 
                          data                    

  P4                      Field research,         Frontend content and
                          policy/legal source     integration
                          verification, testing,  
                          PDF/QR, demo and        
                          business validation     
  -----------------------------------------------------------------------

Every critical module must have an owner and a backup. P4 must not
become "the person who only makes slides"; field validation and test
execution are real engineering work.

## 19.2 Week-by-week plan

### Week 1 --- Scope and foundation

-   Confirm the old-gold exchange workflow.
-   Interview at least 3 jewellers and 5 potential customers.
-   Define data dictionary, state machine and policy schema.
-   Create FastAPI and React skeleton.
-   Create SQLite schema and migration strategy.
-   Implement shop/staff roles.
-   Build item intake and manual evidence entry.
-   Prepare synthetic fixtures, visibly labelled.

**Exit criterion:** create an exchange and store item, weight and
evidence records.

### Week 2 --- Evidence and deterministic calculation

-   Implement HUID record entry/lookup adapter.
-   Implement OCR for bills with field-level confidence.
-   Implement instrument reading capture and human confirmation.
-   Implement evidence grades and consistency rules.
-   Implement integer money engine and golden test vectors.
-   Build quote screen with itemised calculations.

**Exit criterion:** upload bill + enter reading + calculate reproducible
quote; conflicts are blocked or routed to review.

### Week 3 --- Receipt and approvals

-   Implement customer review screen.
-   Implement staff and customer approval events.
-   Implement canonical JSON and SHA-256.
-   Implement amendment chain.
-   Implement QR verification page.
-   Implement receipt PDF and customer explanation.

**Exit criterion:** both parties approve the same receipt hash and the
verifier detects a modified record.

### Week 4 --- Ledgers and jeweller value

-   Implement separate fine-gold and financial ledgers.
-   Implement settlement posting.
-   Implement day-close reconciliation.
-   Implement HUID register exceptions.
-   Implement policy versioning and deduction caps.
-   Add customer Gold Passport.

**Exit criterion:** one complete transaction posts balanced journals and
appears in day close.

### Week 5 --- Sharing and consumer extensions

-   Implement scoped expiring share.
-   Implement Second Opinion as a separate review event.
-   Generate Loan Readiness Pack PDF.
-   Add Consumer Rights Card with official sources and review date.
-   Add offline/manual fallback paths.
-   Conduct usability tests.

**Exit criterion:** customer can share a limited record, receive a
separate opinion and export a clearly qualified loan-readiness pack.

### Week 6 --- Hardening and demo

-   Run unit, integration, property and misuse tests.
-   Fix critical defects.
-   Test with low-end Android browser and weak network.
-   Test AI/OCR failure paths.
-   Prepare two real-world-inspired scenarios plus a clearly labelled
    synthetic scenario.
-   Rehearse a 3--4 minute demo.
-   Prepare architecture, limitations and competitor slides.
-   Freeze features; no risky new module after the freeze date.

**Exit criterion:** reliable end-to-end demo, tested arithmetic, clear
limitations and reproducible setup.

## 19.3 Explicitly out of scope for six weeks

-   Production lender API integration.
-   Real-time BIS private API integration without permission and
    documentation.
-   Automated purity classification from gold photographs.
-   A trained purity prediction CNN.
-   AS7341-based karatage claims.
-   Blockchain.
-   Multi-shop national marketplace.
-   Production payment processing.
-   Complex tax computation.
-   Automated legal advice.
-   Full ERP replacement.

------------------------------------------------------------------------

# 20. Testing and validation

## 20.1 Test-first strategy

The test harness is more important than animations or advanced
dashboards.

  -----------------------------------------------------------------------
  Test class              Example                 Pass condition
  ----------------------- ----------------------- -----------------------
  Money golden tests      Worked examples and     Exact integer result
                          boundary values         

  Unit tests              mg-to-µg, permille,     No unit drift
                          paise conversions       

  Rounding tests          Half-paise boundaries   Documented half-up
                                                  behaviour

  Property tests          Random valid inputs     No negative weight;
                                                  deterministic result

  Evidence tests          Hallmark/bill mismatch  Correct conflict state

  Instrument tests        Spread exceeds          Repeat/assay route
                          configured threshold    

  State tests             Attempt settlement      Rejected
                          before co-sign          

  Ledger tests            Random transaction      Each journal balances
                          sequences               in its own unit

  Reconciliation tests    Missing sale or stock   Exception raised
                          movement                

  Hash tests              Change one canonical    Hash changes
                          field                   

  Amendment tests         Modify locked receipt   Original retained;
                                                  amendment linked

  Permission tests        Shop A reads Shop B     Access denied
                          data                    

  Share tests             Expired/revoked token   Access denied

  Demo isolation          Demo receipt enters     Impossible
                          real ledger             

  OCR tests               Blurry/rotated bills    Field confidence and
                          and displays            correction flow work

  Usability tests         Customer explains       Comprehension measured,
                          deduction               not assumed
  -----------------------------------------------------------------------

## 20.2 Metrics to measure

Do not invent targets before baseline testing. Record:

-   OCR exact-field accuracy by field.
-   Display-digit exact accuracy.
-   Human correction rate.
-   False conflict rate.
-   Missed conflict rate on curated test cases.
-   Quote completion time.
-   Customer comprehension rate.
-   Percentage of transactions with complete evidence.
-   Day-close reconciliation time.
-   App crash/error rate.
-   Share-link access failures.
-   Staff onboarding time.

For any model, report the dataset size, source, labels, split method,
class balance and evaluation limitations.

## 20.3 Field validation hypotheses

  -----------------------------------------------------------------------
  Hypothesis              How to test             Decision if false
  ----------------------- ----------------------- -----------------------
  Customers want an       Ask customers to        Simplify or change the
  itemised explanation    explain a sample        presentation
                          receipt                 

  Jewellers value         Interview and observe   Reduce friction or
  co-signed evidence      actual counter workflow focus on reconciliation

  Daily checks are        Observe shop opening    Make check capture
  feasible                routine                 faster or integrate
                                                  existing process

  HUID lookup is usable   Test permitted public   Keep manual evidence
  in practice             workflow with shops     attachment

  Second Opinion is       Interview both          Keep it as an optional
  trusted                 reviewers and customers document review

  Loan pack helps         Ask lenders what        Keep as customer
  customers               documents they actually organiser, not lender
                          accept                  integration
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 21. Demo plan (3--4 minutes)

Use synthetic data that is visibly marked as demo data. Never imply that
a fabricated customer, instrument reading or lender integration is real.

## Scenario 1 --- Transparent transaction (60 seconds)

1.  Start a demo exchange.
2.  Capture item and weight.
3.  Enter three illustrative instrument readings.
4.  Show source, tolerance and daily check status.
5.  Show the rate snapshot and deduction schedule.
6.  Generate itemised quote.
7.  Customer reviews the same numbers and approves.
8.  Jeweller approves.
9.  Show identical receipt hash on both views.

**Judge takeaway:** both parties can inspect the same calculation and
record.

## Scenario 2 --- Evidence conflict (60--75 seconds)

1.  Load a demo bill with declared purity.
2.  Load a HUID result with a conflicting marked purity.
3.  Run validation.
4.  Show `CONFLICT`, not an accusation or guessed purity.
5.  Show the source values and next action: additional inspection or
    assay.
6.  Attempt instant settlement; system blocks it.

**Judge takeaway:** the system knows when it does not know.

## Scenario 3 --- Tamper attempt and day close (60 seconds)

1.  Open a locked receipt.
2.  Attempt to change a reading.
3.  Show that overwrite is blocked.
4.  Create a linked amendment proposal.
5.  Show original and amended versions.
6.  Post settlement.
7.  Open day close and show gold and money ledgers separately.
8.  Inject a missing stock movement in the test environment and show an
    exception.

**Judge takeaway:** integrity, accountability and operational
usefulness.

## Optional final 20 seconds --- Customer reuse

Show a scoped Second Opinion link or Loan Readiness Pack. Explain that
the reviewer/lender receives only authorised fields and still performs
their own assessment.

------------------------------------------------------------------------

# 22. Risk register

  -------------------------------------------------------------------------------
  Risk            Likelihood     Impact         Mitigation      MVP response
  --------------- -------------- -------------- --------------- -----------------
  Jewellers       Medium/high    Critical       Co-design,      Pilot before
  reject extra                                  reduce steps,   adding features
  workflow                                      demonstrate     
                                                shop value      

  HUID            High           Medium         Manual lookup   Mark unavailable,
  service/API                                   adapter and     never fabricate
  unavailable                                   source          
                                                attachment      

  OCR errors      High           Medium         Field-level     Manual correction
                                                confidence and  
                                                confirmation    

  Instrument      Medium         High           Provenance,     State limitation
  readings                                      checks,         openly
  manipulated                                   multi-point     
                                                protocol, audit 

  Photos mistaken Medium         High           UI and          No photo purity
  for purity                                    documentation   model
  proof                                         restrictions    

  Ledger          Medium         Critical       Separate units, Block settlement
  accounting                                    property tests, on imbalance
  defect                                        immutable       
                                                postings        

  Signature       Medium         High           Accurate        Call it
  misunderstood                                 terminology and authenticated
  legally                                       legal review    approval event

  Privacy breach  Medium         Critical       Data            No public
                                                minimisation,   personal data
                                                access control, 
                                                expiry          

  False trust     High if model  High           No uncalibrated Rule outcomes
  score           rushed                        score           only

  Hardware delay  Medium         Low            Hardware        Drop it
                                                optional        

  Lender          High           Low            PDF evidence    No mock presented
  integration                                   pack            as real
  unavailable                                                   

  Competitor      Medium         High           Competitor      Narrow
  already offers                                sweep and       differentiation
  similar                                       interviews      claim
  features                                                      

  Legal rules     Medium         High           Official source Rights card can
  change                                        links and       be updated
                                                review date     
  -------------------------------------------------------------------------------

------------------------------------------------------------------------

# 23. Trade-off analysis

The design deliberately chooses reliability and explainability over
maximum feature count. The following trade-offs are explicit and should
be defended to judges.

## 23.1 Software-first vs hardware-first

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  Hardware-first    Direct sensor     Calibration,      Reject for MVP
                    capture; visually component         
                    impressive;       reliability,      
                    potential         sensor validity,  
                    reduction in      integration time, 
                    manual entry      field maintenance 

  Software-first    Buildable, works  Depends on staff  **Choose**
  with manual       with existing     entering correct  
  instrument        shop equipment,   readings; does    
  evidence          lower cost,       not independently 
                    supports offline  validate          
                    valuation         instrument output 

  Software +        Extensible; can   Requires          Later phase
  optional          automate weight   calibration and   
  validated         capture later     hardware testing  
  hardware adapter                                      
  -----------------------------------------------------------------------

**Why:** the problem is not merely lack of sensors. It is lack of shared
evidence, understandable arithmetic and traceable records. Hardware is
useful only when it adds valid evidence.

## 23.2 Deterministic rules vs ML trust score

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  One ML score      Simple marketing; Needs labelled    Reject
                    compact UI        ground truth;     
                                      opaque; may       
                                      create false      
                                      certainty         

  Deterministic     Reproducible,     Less visually     **Choose for
  rules and         explainable,      dramatic; rules   MVP**
  evidence states   testable,         need maintenance  
                    auditable                           

  Hybrid rules +    Can prioritise    Requires          Later phase
  calibrated model  review once data  validated dataset 
                    exists            and ongoing       
                                      monitoring        
  -----------------------------------------------------------------------

**Why:** a model cannot manufacture ground truth. Rule outcomes are more
defensible for a six-week prototype.

## 23.3 Photo analysis vs instrument evidence

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  Photo-based       Easy consumer     Visible           Reject
  purity classifier interaction       appearance does   
                                      not establish     
                                      elemental         
                                      composition;      
                                      dataset bias and  
                                      false reassurance 

  Instrument        Based on actual   Instrument can be **Choose**
  readings with     measurement       misused or        
  provenance        method            uncalibrated      

  Photos for OCR,   Useful AI;        Still requires    **Choose**
  display reading   feasible; honest  human             
  and custody       scope             confirmation      
  -----------------------------------------------------------------------

## 23.4 One ledger vs two ledgers

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  One mixed ledger  Fewer tables and  Gold grams and    Reject
                    simpler initial   rupees cannot     
                    coding            meaningfully      
                                      balance in the    
                                      same accounting   
                                      unit              

  Separate gold and Correct unit      More              **Choose**
  financial         discipline;       implementation    
  journals linked   clearer           and testing       
  by transaction    reconciliation                      
  -----------------------------------------------------------------------

## 23.5 Blockchain vs append-only audit log

  ------------------------------------------------------------------------------
  Option                   Benefits          Costs / risks     Decision
  ------------------------ ----------------- ----------------- -----------------
  Blockchain               Distributed       Complexity, cost, Reject
                           consensus in some governance and no 
                           multi-party       guarantee that    
                           settings          input evidence is 
                                             true              

  Database audit log +     Simple,           Depends on        **Choose for
  signed daily manifest    inspectable,      operator and      MVP**
                           adequate for MVP  storage controls; 
                                             not independently 
                                             immutable by      
                                             itself            

  External                 Stronger          Service           Later phase
  timestamp/transparency   independent       dependency and    
  service                  evidence of       integration       
                           existence at a    effort            
                           time                                
  ------------------------------------------------------------------------------

## 23.6 Monolith vs microservices

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  Microservices     Independent       More              Reject for MVP
                    scaling and       infrastructure,   
                    deployment        contracts,        
                                      observability and 
                                      failure modes     

  Modular monolith  Clear modules,    Requires          **Choose**
                    one deployable    discipline to     
                    app, simple       preserve module   
                    testing           boundaries        
  -----------------------------------------------------------------------

## 23.7 SQLite vs PostgreSQL

  ------------------------------------------------------------------------
  Option            Benefits          Costs / risks      Decision
  ----------------- ----------------- ------------------ -----------------
  SQLite            Zero-config,      Limited            **Choose for
                    reliable local    concurrent-write   local prototype**
                    demo, easy backup throughput and     
                                      multi-user         
                                      deployment         
                                      suitability        

  PostgreSQL        Better multi-user More setup and     Production
                    concurrency,      deployment         migration
                    operational       overhead           
                    controls and                         
                    production path                      
  ------------------------------------------------------------------------

Do not claim SQLite has no concurrency concerns. Design repository and
transaction boundaries so migration is possible.

## 23.8 Customer phone signature vs assisted approval

  ---------------------------------------------------------------------------
  Option            Benefits              Costs / risks     Decision
  ----------------- --------------------- ----------------- -----------------
  Mandatory         Stronger              Excludes some     Reject
  customer          customer-controlled   customers;        
  smartphone        review                network and       
                                          device barriers   

  OTP               Familiar and          Phone ownership   Support
                    practical             and OTP delivery  
                                          issues; does not  
                                          by itself         
                                          establish a       
                                          qualified digital 
                                          signature         

  Assisted PIN /    Inclusive and fast    Lower assurance;  Support with
  counter device                          staff coercion or explicit label
                                          collusion risk    and audit

  Customer's own    Better control and    More steps and    Preferred route
  device +          review                device dependence 
  authenticated                                             
  approval                                                  
  ---------------------------------------------------------------------------

## 23.9 Public verification vs private customer vault

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  Public full       Easy sharing      Exposes identity, Reject
  receipt                             assets and        
                                      transaction       
                                      details           

  Private vault     Strong privacy    Third parties     Incomplete
  only                                cannot easily     
                                      verify integrity  

  Public minimal    Balances          More permission   **Choose**
  verification +    integrity and     and token logic   
  private scoped    privacy                             
  share                                                 
  -----------------------------------------------------------------------

## 23.10 Instant settlement vs assay hold

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  Always instant    Fast and simple   Higher risk when  Reject as
                                      evidence is       universal rule
                                      incomplete or     
                                      conflicting       

  Always assay      Stronger          Slow, costly,     Reject as
                    composition       operationally     universal rule
                    evidence for      burdensome        
                    tested sample                       

  Instant only when Practical and     Requires clear    **Choose**
  configured        risk-based        thresholds and    
  evidence                            customer          
  conditions pass;                    explanation       
  otherwise                                             
  hold/assay                                            
  -----------------------------------------------------------------------

## 23.11 Broad feature set vs narrow MVP

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  Build every v4    Bigger feature    Thin              Reject
  feature           list and pitch    implementation,   
                                      integration risk, 
                                      unvalidated       
                                      claims            

  Build one         Strong end-to-end Fewer screens and **Choose**
  complete exchange proof; easier     integrations in   
  workflow          testing           demo              

  Add Passport,     Demonstrates      Must preserve     Include only
  Second Opinion    extensibility     scope and privacy after core
  and Loan Pack as                                      workflow works
  exports from the                                      
  same record                                           
  -----------------------------------------------------------------------

## 23.12 Paid jeweller badge vs evidence-based reviewer verification

  -----------------------------------------------------------------------
  Option            Benefits          Costs / risks     Decision
  ----------------- ----------------- ----------------- -----------------
  Subscription buys Revenue           Pay-to-trust      Reject
  "verified" badge                    conflict; damages 
                                      neutrality        

  Published         More credible     Requires          Choose if network
  criteria,         trust signal      governance and    launches
  credentials and                     moderation        
  review history                                        

  No reviewer badge Lowest risk       Less network      **Choose for
  in MVP                              marketing         MVP**
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 24. Business and impact measurement

Do not present unverified national loss estimates as fact.

Measure the project's impact through pilot outcomes:

-   Percentage of customers who can explain the rate, deduction and
    payable amount after viewing the receipt.
-   Percentage of transactions with complete evidence provenance.
-   Number of valuation disputes resolved using the shared record.
-   Average time required to produce a complete transaction record.
-   Percentage of daily stock movements reconciled.
-   Number of amendments visible to both parties.
-   Number of customers successfully sharing a scoped evidence pack.
-   Jeweller willingness to continue after a pilot.

Social impact should be framed as improved access to understandable
transaction evidence and complaint information---not as a proven
reduction in national gold fraud until measured.

------------------------------------------------------------------------

# 25. Judge questions and defensible answers

**Q1. Does Gold Trust AI detect whether gold is real?**

No. It does not certify gold purity. It organises and checks consistency
across available evidence, including instrument readings and hallmark
records. Conflicts are routed to additional inspection or assay.

**Q2. Why use AI if the valuation is deterministic?**

AI reduces friction in extracting bill fields, reading instrument
displays and explaining receipt lines. The money engine remains
deterministic so that every amount is reproducible.

**Q3. What if the jeweller enters a fake reading?**

The system cannot guarantee that an input measurement is honest. It
records instrument identity, operator, timestamp, check status, display
evidence and amendments. Independent assay remains the escalation route.

**Q4. Does a valid HUID prove the item is currently 22K?**

It proves that the HUID lookup returned a registered hallmark record
with the stated details. It does not establish that the article has not
been altered after hallmarking or that every part of the present item
has the same composition.

**Q5. Why not use blockchain?**

The core need is to preserve a shared record and detect later changes. A
canonical receipt, authenticated approvals and an append-only audit
trail are simpler for the MVP. Blockchain would not prove that the
original reading was true.

**Q6. Why would a jeweller adopt this?**

The value proposition is better documentation, transparent customer
explanation, fewer repeat disputes and traceable stock reconciliation.
We are validating this with shopkeepers rather than assuming adoption.

**Q7. Can lenders accept the Loan Readiness Pack?**

The pack is a customer-controlled evidence summary. It is not a
lender-approved appraisal. A lender may use it as supporting information
but performs its own checks.

**Q8. What is genuinely innovative?**

The innovation is the integrated workflow: evidence provenance,
cross-source consistency, deterministic valuation, authenticated
two-party approval, separate gold and money ledgers, and
customer-controlled reuse of the same transaction record.

**Q9. What happens without internet?**

Manual evidence entry and deterministic valuation can work locally.
External HUID lookup, messaging and independent anchoring may be
unavailable and are marked accordingly. The system never fabricates a
successful verification.

**Q10. What is your biggest limitation?**

The platform cannot independently guarantee the correctness of an
instrument reading or certify the composition of an entire article. It
makes the evidence, process, calculation and uncertainty visible and
provides an assay escalation path.

------------------------------------------------------------------------

# 26. Final product scope

## Must ship

-   Counter intake.
-   Manual instrument and scale reading capture.
-   HUID evidence attachment / permitted lookup workflow.
-   Bill OCR with human confirmation.
-   Evidence grades and deterministic consistency rules.
-   Conflict state and assay escalation.
-   Integer-based valuation engine.
-   Versioned deduction policy.
-   Customer and jeweller authenticated approvals.
-   Canonical receipt and SHA-256 integrity check.
-   Amendment history.
-   Gold inventory ledger.
-   Separate financial ledger.
-   Day-close reconciliation.
-   QR verification with minimal public data.
-   Gold Passport export.
-   Demo-mode isolation.
-   Automated test suite.

## Should ship if core is stable

-   Receipt explainer in two languages.
-   Consumer Rights Card with reviewed official links.
-   Scoped expiring Second Opinion share.
-   Loan Readiness Pack PDF.
-   Display OCR.
-   Shop policy transparency page.

## Later

-   Production lender integration.
-   Real BIS integration where an authorised interface exists.
-   Bluetooth instrument integrations.
-   Validated hardware scale adapter.
-   Multi-shop network.
-   Advanced analytics.
-   Calibrated anomaly model based on real labelled data.
-   Production-grade external transparency log.

## Explicitly out of scope

-   Photo-based purity prediction.
-   Automatic gold certification.
-   AI-set prices.
-   Automatic legal advice.
-   Guaranteed lender acceptance.
-   Unsupported fraud-loss claims.
-   Unvalidated sensor purity claims.
-   Blockchain for appearance.

------------------------------------------------------------------------

# 27. Final recommendation

Gold Trust AI should be positioned as a **two-party evidence and
transaction-integrity platform for jewellery**, not as an AI that can
identify pure or impure gold from a phone camera.

The winning product is not the one with the most AI models or the
longest feature list. It is the one that can demonstrate a complete,
correct and useful transaction:

1.  A customer brings an item.
2.  The jeweller records the weight and available evidence.
3.  The system identifies missing or conflicting information.
4.  The deterministic engine calculates the quote transparently.
5.  Both parties review and approve the same record.
6.  The system posts the gold and financial movements separately.
7.  The customer keeps a private Passport and can share selected
    evidence later.
8.  The jeweller can reconcile the transaction in the shop's daily
    records.

**The core competitive claim:**

> Gold Trust AI does not ask customers to trust an AI verdict. It gives
> customers and jewellers the same evidence, the same calculation, the
> same approved receipt and a record they can verify later.

That is the product to build, test and defend.

------------------------------------------------------------------------

# Appendix A --- Assumption register

Every assumption must be labelled and validated before being promoted to
a fact.

  -----------------------------------------------------------------------
  Assumption              Validation method       Owner
  ----------------------- ----------------------- -----------------------
  Small jewellers will    Observe and interview   P4
  use a co-signed         3--5 shops              
  workflow                                        

  Customers understand    Comprehension test      P2/P4
  itemised deductions                             
  better                                          

  Manual instrument entry Counter workflow pilot  P1/P4
  is acceptable for MVP                           

  HUID lookup is          Test current permitted  P4
  accessible in the       BIS route               
  shop's real workflow                            

  OCR is useful on local  Build representative    P3
  bills                   test set                

  Shop policy can be      Interview shop owners   P4
  expressed in a                                  
  structured schedule                             

  Daily reconciliation    Compare current process P1/P4
  creates value           with prototype          

  Lenders will use a      Interview lender staff; P4
  readiness pack          no assumed integration  

  Customers want Second   Customer interviews and P2/P4
  Opinion                 usage test              
  -----------------------------------------------------------------------

# Appendix B --- Release acceptance checklist

-   [ ] A complete exchange can be created without AI.
-   [ ] All weights are stored in integer mg.
-   [ ] Purity is stored in integer permille.
-   [ ] Money is stored in integer paise.
-   [ ] The worked example reproduces exactly.
-   [ ] Every displayed value has a source.
-   [ ] Missing evidence is shown as unknown.
-   [ ] Conflicting evidence blocks instant settlement under the
    configured policy.
-   [ ] Customer and jeweller approve the same receipt hash.
-   [ ] A post-lock edit creates an amendment.
-   [ ] Gold and money ledgers balance independently.
-   [ ] Day close flags injected discrepancies.
-   [ ] Public QR reveals no personal information.
-   [ ] Expired and revoked shares cannot be accessed.
-   [ ] Second Opinion does not rewrite the original result.
-   [ ] Loan Readiness Pack says it is not a certified appraisal.
-   [ ] Consumer rights content has an official source and review date.
-   [ ] Demo data is visibly marked and isolated.
-   [ ] OCR failure has a manual fallback.
-   [ ] Internet failure does not fabricate external verification.
-   [ ] The team can reproduce the demo from a clean setup.

# Appendix C --- Source and legal verification policy

Before submission and again before public deployment, verify all current
claims using primary sources:

1.  BIS hallmarking and HUID guidance, including current scope,
    exemptions and consumer complaint process.
2.  BIS Care app and current permitted HUID verification route.
3.  Applicable BIS compensation provisions and the exact remedy
    language.
4.  Current National Consumer Helpline contact and complaint process.
5.  Current Indian data protection law/rules and effective obligations.
6.  Applicable Legal Metrology requirements for weighing instruments.
7.  Applicable tax and invoice requirements, reviewed by a qualified
    professional.
8.  Current gold-rate source methodology, purity basis, city and
    timestamp.
9.  Current lender appraisal and document acceptance requirements.

For every source, record URL, issuing authority, access date, relevant
section and the exact claim supported. Do not rely on an unattributed
statistic, an industry estimate presented as official data or a future
feature described as already live.

**End of specification.**
