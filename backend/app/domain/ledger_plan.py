"""Pure domain posting planner for balanced dual-entry ledgers.

Per ADR-0018 and §6.5:
Two distinct ledgers:
1. Gold Ledger: Denominated in micrograms (Ug).
   - Debit: Stock:OldGold
   - Credit: Customer:GoldPayable
   - Credit: Retained:Deduction
   - Discharge by settlement:
     - Debit: Customer:GoldPayable
     - Credit: Settlement:GoldToCash (clearing account)

2. Money Ledger: Denominated in paise (Paise).
   - Debit: Purchases:OldGold (exact calculated paise)
   - Debit/Credit: RoundingDifference (signed paise difference to whole rupee)
   - Credit: Customer:CashPayable (settlement amount)
   - Discharge:
     - Debit: Customer:CashPayable
     - Credit: Cash / Bank

Every entry must have sum(Debits) == sum(Credits) and at least 2 lines.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from app.domain.exceptions import DomainError
from app.domain.units import Paise, Ug, validate_paise, validate_ug


class LedgerBalanceError(DomainError):
    """Raised when journal entries fail debit == credit balance."""

    def __init__(self, message: str, entry_name: str, debit_sum: int, credit_sum: int) -> None:
        super().__init__(message, code="UNBALANCED_JOURNAL_ENTRY")
        self.entry_name = entry_name
        self.debit_sum = debit_sum
        self.credit_sum = credit_sum


@dataclass(frozen=True, slots=True)
class GoldJournalLine:
    account: str
    side: Literal["D", "C"]
    amount_ug: Ug


@dataclass(frozen=True, slots=True)
class GoldJournalEntry:
    entry_name: str
    description: str
    lines: tuple[GoldJournalLine, ...]

    def assert_balanced(self) -> None:
        debits = sum(int(line.amount_ug) for line in self.lines if line.side == "D")
        credits_total = sum(int(line.amount_ug) for line in self.lines if line.side == "C")
        if debits != credits_total or len(self.lines) < 2:
            raise LedgerBalanceError(
                f"Gold entry '{self.entry_name}' unbalanced: D={debits} != C={credits_total}",
                self.entry_name,
                debits,
                credits_total,
            )


@dataclass(frozen=True, slots=True)
class MoneyJournalLine:
    account: str
    side: Literal["D", "C"]
    amount_paise: Paise


@dataclass(frozen=True, slots=True)
class MoneyJournalEntry:
    entry_name: str
    description: str
    lines: tuple[MoneyJournalLine, ...]

    def assert_balanced(self) -> None:
        debits = sum(int(line.amount_paise) for line in self.lines if line.side == "D")
        credits_total = sum(int(line.amount_paise) for line in self.lines if line.side == "C")
        if debits != credits_total or len(self.lines) < 2:
            raise LedgerBalanceError(
                f"Money entry '{self.entry_name}' unbalanced: D={debits} != C={credits_total}",
                self.entry_name,
                debits,
                credits_total,
            )


@dataclass(frozen=True, slots=True)
class PostingPlan:
    """Complete balanced posting set for an exchange transaction."""

    exchange_id: str
    receipt_hash: str
    gold_intake: GoldJournalEntry
    gold_discharge: GoldJournalEntry
    money_payable: MoneyJournalEntry
    money_payout: MoneyJournalEntry


def plan_postings(receipt: Mapping[str, Any], payment_method: str = "Cash") -> PostingPlan:
    """Generate and validate all dual-ledger journal postings for a finalized receipt."""
    exchange_id = receipt["exchange_id"]
    r_hash = receipt.get("receipt_hash", "0" * 64)

    val = receipt["valuation"]
    fine_gold_ug = validate_ug(val["fine_gold_ug"])
    payable_gold_ug = validate_ug(val["payable_gold_ug"])
    retained_gold_ug = validate_ug(val["retained_gold_ug"])

    exact_value_paise = validate_paise(val["exact_value_paise"])
    settlement_paise = validate_paise(val["settlement_paise"])
    rounding_diff_paise = val["rounding_difference_paise"]

    # --- 1. Gold Intake Entry ---
    # Debit: Stock:OldGold (total fine gold)
    # Credit: Customer:GoldPayable (gold owed to customer)
    # Credit: Retained:Deduction (shop melting/refining margin)
    gold_intake_lines: list[GoldJournalLine] = [
        GoldJournalLine(account="Stock:OldGold", side="D", amount_ug=fine_gold_ug),
        GoldJournalLine(account="Customer:GoldPayable", side="C", amount_ug=payable_gold_ug),
    ]
    if int(retained_gold_ug) > 0:
        gold_intake_lines.append(
            GoldJournalLine(account="Retained:Deduction", side="C", amount_ug=retained_gold_ug)
        )
    gold_intake = GoldJournalEntry(
        entry_name="Gold:Intake",
        description=f"Old gold intake for exchange {exchange_id}",
        lines=tuple(gold_intake_lines),
    )
    gold_intake.assert_balanced()

    # --- 2. Gold Discharge Entry ---
    # Customer obligation discharged into settlement clearing
    # Debit: Customer:GoldPayable
    # Credit: Settlement:GoldToCash
    gold_discharge = GoldJournalEntry(
        entry_name="Gold:Discharge",
        description=f"Gold obligation discharged into financial settlement for {exchange_id}",
        lines=(
            GoldJournalLine(account="Customer:GoldPayable", side="D", amount_ug=payable_gold_ug),
            GoldJournalLine(account="Settlement:GoldToCash", side="C", amount_ug=payable_gold_ug),
        ),
    )
    gold_discharge.assert_balanced()

    # --- 3. Money Payable Entry ---
    # Debit: Purchases:OldGold (exact valuation)
    # Debit/Credit: RoundingDifference (balancing figure for rupee settlement)
    # Credit: Customer:CashPayable (settlement amount)
    money_payable_lines: list[MoneyJournalLine] = [
        MoneyJournalLine(account="Purchases:OldGold", side="D", amount_paise=exact_value_paise),
    ]

    # Handle rounding difference:
    # settlement_paise = exact_value_paise + rounding_diff_paise
    # If diff > 0 (+24p): Debit RoundingDifference -> total Debits = settlement
    # If diff < 0 (-38p): Credit RoundingDifference -> total Credits = exact value
    if rounding_diff_paise > 0:
        money_payable_lines.append(
            MoneyJournalLine(
                account="RoundingDifference",
                side="D",
                amount_paise=validate_paise(rounding_diff_paise),
            )
        )
    elif rounding_diff_paise < 0:
        money_payable_lines.append(
            MoneyJournalLine(
                account="RoundingDifference",
                side="C",
                amount_paise=validate_paise(abs(rounding_diff_paise)),
            )
        )

    money_payable_lines.append(
        MoneyJournalLine(account="Customer:CashPayable", side="C", amount_paise=settlement_paise)
    )

    money_payable = MoneyJournalEntry(
        entry_name="Money:PayableCreated",
        description=f"Payable locked for exchange {exchange_id}",
        lines=tuple(money_payable_lines),
    )
    money_payable.assert_balanced()

    # --- 4. Money Payout Entry ---
    # Discharge payable to cash or bank
    # Debit: Customer:CashPayable
    # Credit: Cash or Bank
    payout_account = "Bank" if payment_method.lower() in ("bank", "upi", "neft") else "Cash"
    money_payout = MoneyJournalEntry(
        entry_name="Money:PayoutDischarge",
        description=f"Payout discharge via {payout_account} for exchange {exchange_id}",
        lines=(
            MoneyJournalLine(
                account="Customer:CashPayable", side="D", amount_paise=settlement_paise
            ),
            MoneyJournalLine(account=payout_account, side="C", amount_paise=settlement_paise),
        ),
    )
    money_payout.assert_balanced()

    return PostingPlan(
        exchange_id=exchange_id,
        receipt_hash=r_hash,
        gold_intake=gold_intake,
        gold_discharge=gold_discharge,
        money_payable=money_payable,
        money_payout=money_payout,
    )
