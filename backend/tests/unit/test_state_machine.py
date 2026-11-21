"""Tests for the pure domain state machine and guards."""

import pytest

from app.domain.exceptions import StateMachineError
from app.domain.state_machine import (
    ExchangeEvent,
    ExchangeState,
    TransitionContext,
    transition,
)


def test_happy_path_lifecycle() -> None:
    """Full lifecycle from DRAFT through CLOSED."""
    state = ExchangeState.DRAFT

    # 1. Lock Intake
    state = transition(state, ExchangeEvent.LOCK_INTAKE)
    assert state == ExchangeState.INTAKE_LOCKED

    # 2. Submit Evidence (requires witness_present=True)
    state = transition(
        state, ExchangeEvent.SUBMIT_EVIDENCE, TransitionContext(witness_present=True)
    )
    assert state == ExchangeState.EVIDENCE_CAPTURED

    # 3. Evaluate Rules (CONSISTENT)
    state = transition(
        state, ExchangeEvent.EVALUATE_RULES, TransitionContext(validation_status="CONSISTENT")
    )
    assert state == ExchangeState.VALIDATION_CLEAR

    # 4. Generate Quote
    state = transition(state, ExchangeEvent.GENERATE_QUOTE)
    assert state == ExchangeState.QUOTED

    # 5. Present to Customer
    state = transition(state, ExchangeEvent.PRESENT_TO_CUSTOMER)
    assert state == ExchangeState.CUSTOMER_REVIEW

    # 6. Cosign (matching hashes)
    test_hash = "a" * 64
    state = transition(
        state,
        ExchangeEvent.COSIGN,
        TransitionContext(customer_hash=test_hash, staff_hash=test_hash),
    )
    assert state == ExchangeState.COSIGNED

    # 7. Begin Settlement
    state = transition(state, ExchangeEvent.BEGIN_SETTLEMENT)
    assert state == ExchangeState.SETTLEMENT_PENDING

    # 8. Complete Settlement (requires balanced postings)
    state = transition(
        state, ExchangeEvent.COMPLETE_SETTLEMENT, TransitionContext(postings_balanced=True)
    )
    assert state == ExchangeState.SETTLED

    # 9. Close Day
    state = transition(state, ExchangeEvent.CLOSE_DAY)
    assert state == ExchangeState.CLOSED


def test_review_required_pathway() -> None:
    """Handling of CONFLICT and INCOMPLETE validation leading to REVIEW_REQUIRED and back."""
    state = ExchangeState.EVIDENCE_CAPTURED

    # Transition to review on CONFLICT
    state = transition(
        state, ExchangeEvent.EVALUATE_RULES, TransitionContext(validation_status="CONFLICT")
    )
    assert state == ExchangeState.REVIEW_REQUIRED

    # Add evidence loops back to EVIDENCE_CAPTURED
    state = transition(state, ExchangeEvent.ADD_EVIDENCE)
    assert state == ExchangeState.EVIDENCE_CAPTURED

    # Re-evaluate with INCOMPLETE
    state = transition(
        state, ExchangeEvent.EVALUATE_RULES, TransitionContext(validation_status="INCOMPLETE")
    )
    assert state == ExchangeState.REVIEW_REQUIRED

    # Request assay loops back to EVIDENCE_CAPTURED
    state = transition(state, ExchangeEvent.REQUEST_ASSAY)
    assert state == ExchangeState.EVIDENCE_CAPTURED


def test_guard_violations() -> None:
    """Verify all guard conditions reject invalid transitions."""
    # Cannot submit evidence without witness
    with pytest.raises(StateMachineError, match="without customer weight witness"):
        transition(
            ExchangeState.INTAKE_LOCKED,
            ExchangeEvent.SUBMIT_EVIDENCE,
            TransitionContext(witness_present=False),
        )

    # Cannot cosign with mismatched hashes
    with pytest.raises(StateMachineError, match="hash mismatch"):
        transition(
            ExchangeState.CUSTOMER_REVIEW,
            ExchangeEvent.COSIGN,
            TransitionContext(customer_hash="hash_a", staff_hash="hash_b"),
        )

    # Cannot complete settlement with unbalanced postings
    with pytest.raises(StateMachineError, match="unbalanced postings"):
        transition(
            ExchangeState.SETTLEMENT_PENDING,
            ExchangeEvent.COMPLETE_SETTLEMENT,
            TransitionContext(postings_balanced=False),
        )


def test_illegal_transitions() -> None:
    """Verify that arbitrary non-edge transitions raise StateMachineError."""
    # Cannot skip straight to SETTLED from DRAFT
    with pytest.raises(StateMachineError, match="Illegal transition"):
        transition(ExchangeState.DRAFT, ExchangeEvent.COMPLETE_SETTLEMENT)

    # Terminal states reject any event
    with pytest.raises(StateMachineError, match="terminal state"):
        transition(ExchangeState.CLOSED, ExchangeEvent.LOCK_INTAKE)

    with pytest.raises(StateMachineError, match="terminal state"):
        transition(ExchangeState.CANCELLED, ExchangeEvent.GENERATE_QUOTE)


def test_cancellation_rules() -> None:
    """Verify that cancellation is allowed from pre-settlement states and forbidden once settled."""
    assert transition(ExchangeState.DRAFT, ExchangeEvent.CANCEL) == ExchangeState.CANCELLED
    assert transition(ExchangeState.INTAKE_LOCKED, ExchangeEvent.CANCEL) == ExchangeState.CANCELLED
    assert transition(ExchangeState.QUOTED, ExchangeEvent.CANCEL) == ExchangeState.CANCELLED
    assert (
        transition(ExchangeState.REVIEW_REQUIRED, ExchangeEvent.CANCEL) == ExchangeState.CANCELLED
    )

    # Once settled, cannot cancel
    with pytest.raises(StateMachineError, match="Cannot cancel from state SETTLED"):
        transition(ExchangeState.SETTLED, ExchangeEvent.CANCEL)
