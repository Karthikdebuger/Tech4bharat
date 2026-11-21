"""Settlement service coordinating dual-ledger journal execution."""

import uuid
from sqlalchemy.orm import Session
from app.domain.ledger_plan import plan_postings
from app.domain.receipt import create_finalized_receipt
from app.domain.state_machine import (
    ExchangeEvent,
    ExchangeState,
    TransitionContext,
    transition,
)
from app.models.entities import ReceiptModel
from app.repos.base import TenantContext
from app.repos.exchange_repo import ExchangeRepository
from app.repos.ledger_repo import LedgerRepository

class SettlementService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def cosign_exchange(
        self,
        tenant: TenantContext,
        exchange_id: uuid.UUID,
        receipt_dict: dict,
        staff_approved_hash: str,
        customer_approved_hash: str,
    ) -> ReceiptModel:
        exchange_repo = ExchangeRepository(self.session, tenant)
        exchange = exchange_repo.get_exchange(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not found")

        # Step 1: Advance state machine from QUOTED -> CUSTOMER_REVIEW -> COSIGNED
        curr = ExchangeState(exchange.state)
        if curr == ExchangeState.QUOTED:
            curr = transition(curr, ExchangeEvent.PRESENT_TO_CUSTOMER)
            exchange = exchange_repo.update_state(exchange_id, curr.value, exchange.version)

        # Cosign requires matching hashes
        ctx = TransitionContext(
            customer_hash=customer_approved_hash,
            staff_hash=staff_approved_hash,
        )
        new_state = transition(curr, ExchangeEvent.COSIGN, ctx)
        exchange = exchange_repo.update_state(exchange_id, new_state.value, exchange.version)

        # Step 2: Persist final immutable receipt
        final_dict, r_hash, _ = create_finalized_receipt(receipt_dict)
        receipt = exchange_repo.save_receipt(
            exchange_id=exchange_id,
            receipt_hash=r_hash,
            canonical_payload=final_dict,
            is_demo=exchange.is_demo,
        )
        return receipt

    def execute_settlement(
        self,
        tenant: TenantContext,
        exchange_id: uuid.UUID,
        payment_method: str = "Cash",
    ) -> dict[str, object]:
        exchange_repo = ExchangeRepository(self.session, tenant)
        ledger_repo = LedgerRepository(self.session, tenant)

        exchange = exchange_repo.get_exchange(exchange_id)
        if not exchange:
            raise ValueError(f"Exchange {exchange_id} not found")

        receipt = exchange.receipt
        if not receipt:
            raise ValueError(f"Cannot settle exchange {exchange_id} without a finalized receipt")

        # Step 1: Transition state: COSIGNED -> SETTLEMENT_PENDING
        curr = ExchangeState(exchange.state)
        curr = transition(curr, ExchangeEvent.BEGIN_SETTLEMENT)
        exchange = exchange_repo.update_state(exchange_id, curr.value, exchange.version)

        # Step 2: Plan double-entry postings
        plan = plan_postings(receipt.canonical_payload, payment_method=payment_method)

        # Step 3: Persist all four balanced entries
        ledger_repo.post_gold_entry(plan.gold_intake, exchange_id=exchange_id, receipt_hash=receipt.receipt_hash)
        ledger_repo.post_gold_entry(plan.gold_discharge, exchange_id=exchange_id, receipt_hash=receipt.receipt_hash)
        ledger_repo.post_money_entry(plan.money_payable, exchange_id=exchange_id, receipt_hash=receipt.receipt_hash)
        ledger_repo.post_money_entry(plan.money_payout, exchange_id=exchange_id, receipt_hash=receipt.receipt_hash)

        # Step 4: Complete settlement: SETTLEMENT_PENDING -> SETTLED
        curr = transition(curr, ExchangeEvent.COMPLETE_SETTLEMENT, TransitionContext(postings_balanced=True))
        exchange = exchange_repo.update_state(exchange_id, curr.value, exchange.version)

        return {
            "status": "SETTLED",
            "settlement_paise": receipt.canonical_payload["valuation"]["settlement_paise"],
            "payable_gold_ug": receipt.canonical_payload["valuation"]["payable_gold_ug"],
            "receipt_hash": receipt.receipt_hash,
        }
