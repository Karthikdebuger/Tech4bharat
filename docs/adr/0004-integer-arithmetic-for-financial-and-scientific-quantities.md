# ADR 0004: Integer Arithmetic for Financial and Scientific Quantities

## Status
Accepted

## Context
Floating point arithmetic (IEEE 754 `float`/`double`) introduces non-deterministic rounding errors, platform-dependent precision variances, and catastrophic cancellation in currency and high-precision precious metal measurements. In precious jewellery valuation, an error of even 0.01g or 1 paisa compromises trust and auditability.

## Decision
All quantities across domain, database, API, and verification layers are strictly stored and computed as signed 64-bit integers:
- **Gross & Net Weight**: Milligrams (`Mg`, $1\text{ mg} = 10^{-3}\text{ g}$).
- **Fine Gold Content**: Micrograms (`Ug`, $1\text{ \mu g} = 10^{-6}\text{ g}$).
- **Purity / Fineness**: Permille (`Permille`, parts per thousand, $0 \dots 1000$).
- **Deductions / Discretionary Margins**: Basis Points (`Bp`, $1\text{ bp} = 0.01\% = 1/10,000$).
- **Market Rates**: Paise per gram (`PaisePerG`, e.g., ₹13,000/g = 1,300,000 paise/g).
- **Monetary Valuations & Ledger Postings**: Paise (`Paise`, $1\text{ INR} = 100\text{ paise}$).

Floating-point types and operations are strictly prohibited in `domain/` and checked automatically via an AST analysis test. Rounding uses half-up integer arithmetic: `(2 * n + d) // (2 * d)`.

## Consequences
- Guaranteed exactness and reproducible arithmetic across Python, TypeScript, and SQL.
- Complete elimination of IEEE 754 precision drift.
- Transparent mathematical explanations verified by independent differential tests.
