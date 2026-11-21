"""State machine and transition guards for Gold Trust AI exchanges.

Per §5.3:
Transitions are data, guarded by pure functions, and tested model-based.
States:
  DRAFT -> INTAKE_LOCKED -> EVIDENCE_CAPTURED -> [VALIDATION_CLEAR | REVIEW_REQUIRED]
  -> QUOTED -> CUSTOMER_REVIEW -> COSIGNED -> SETTLEMENT_PENDING -> SETTLED -> CLOSED
  (or CANCELLED from applicable non-terminal states)
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from app.domain.exceptions import StateMachineError


class ExchangeState(StrEnum):
    DRAFT = "DRAFT"
    INTAKE_LOCKED = "INTAKE_LOCKED"
    EVIDENCE_CAPTURED = "EVIDENCE_CAPTURED"
    VALIDATION_CLEAR = "VALIDATION_CLEAR"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    QUOTED = "QUOTED"
    CUSTOMER_REVIEW = "CUSTOMER_REVIEW"
    COSIGNED = "COSIGNED"
    SETTLEMENT_PENDING = "SETTLEMENT_PENDING"
    SETTLED = "SETTLED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class ExchangeEvent(StrEnum):
    LOCK_INTAKE = "lock_intake"
    SUBMIT_EVIDENCE = "submit_evidence"
    EVALUATE_RULES = "evaluate_rules"
    ADD_EVIDENCE = "add_evidence"
    REQUEST_ASSAY = "request_assay"
    GENERATE_QUOTE = "generate_quote"
    PRESENT_TO_CUSTOMER = "present_to_customer"
    COSIGN = "cosign"
    BEGIN_SETTLEMENT = "begin_settlement"
    COMPLETE_SETTLEMENT = "complete_settlement"
    CLOSE_DAY = "close_day"
    CANCEL = "cancel"


TERMINAL_STATES: Final[frozenset[ExchangeState]] = frozenset(
    {
        ExchangeState.CLOSED,
        ExchangeState.CANCELLED,
    }
)

CANCELLABLE_STATES: Final[frozenset[ExchangeState]] = frozenset(
    {
        ExchangeState.DRAFT,
        ExchangeState.INTAKE_LOCKED,
        ExchangeState.EVIDENCE_CAPTURED,
        ExchangeState.VALIDATION_CLEAR,
        ExchangeState.REVIEW_REQUIRED,
        ExchangeState.QUOTED,
        ExchangeState.CUSTOMER_REVIEW,
    }
)


@dataclass(frozen=True, slots=True)
class TransitionContext:
    """Contextual metadata passed to transition guards."""

    validation_status: str | None = None  # "CONSISTENT", "CONFLICT", "INCOMPLETE"
    witness_present: bool = False
    customer_hash: str | None = None
    staff_hash: str | None = None
    postings_balanced: bool = False


def transition(
    current_state: ExchangeState,
    event: ExchangeEvent,
    context: TransitionContext | None = None,
) -> ExchangeState:
    """Evaluate pure state machine transition with guard conditions.

    Raises:
        StateMachineError: If transition is illegal or guard condition fails.
    """
    ctx = context or TransitionContext()

    if current_state in TERMINAL_STATES:
        raise StateMachineError(
            f"Cannot transition from terminal state {current_state}",
            current_state=current_state,
            event=event,
        )

    # Universal cancellation guard
    if event == ExchangeEvent.CANCEL:
        if current_state in CANCELLABLE_STATES:
            return ExchangeState.CANCELLED
        raise StateMachineError(
            f"Cannot cancel from state {current_state}",
            current_state=current_state,
            event=event,
        )

    match current_state:
        case ExchangeState.DRAFT:
            if event == ExchangeEvent.LOCK_INTAKE:
                return ExchangeState.INTAKE_LOCKED

        case ExchangeState.INTAKE_LOCKED:
            if event == ExchangeEvent.SUBMIT_EVIDENCE:
                if not ctx.witness_present:
                    raise StateMachineError(
                        "Cannot submit evidence without customer weight witness entry",
                        current_state=current_state,
                        event=event,
                    )
                return ExchangeState.EVIDENCE_CAPTURED

        case ExchangeState.EVIDENCE_CAPTURED:
            if event == ExchangeEvent.EVALUATE_RULES:
                if ctx.validation_status == "CONSISTENT":
                    return ExchangeState.VALIDATION_CLEAR
                if ctx.validation_status in ("CONFLICT", "INCOMPLETE"):
                    return ExchangeState.REVIEW_REQUIRED
                raise StateMachineError(
                    f"Invalid validation status '{ctx.validation_status}' for rule evaluation",
                    current_state=current_state,
                    event=event,
                )

        case ExchangeState.REVIEW_REQUIRED:
            if event == ExchangeEvent.ADD_EVIDENCE:
                return ExchangeState.EVIDENCE_CAPTURED
            if event == ExchangeEvent.REQUEST_ASSAY:
                return ExchangeState.EVIDENCE_CAPTURED

        case ExchangeState.VALIDATION_CLEAR:
            if event == ExchangeEvent.GENERATE_QUOTE:
                return ExchangeState.QUOTED

        case ExchangeState.QUOTED:
            if event == ExchangeEvent.PRESENT_TO_CUSTOMER:
                return ExchangeState.CUSTOMER_REVIEW

        case ExchangeState.CUSTOMER_REVIEW:
            if event == ExchangeEvent.COSIGN:
                if not ctx.customer_hash or not ctx.staff_hash:
                    raise StateMachineError(
                        "Cosigning requires both staff and customer approval hashes",
                        current_state=current_state,
                        event=event,
                    )
                if ctx.customer_hash != ctx.staff_hash:
                    msg = (
                        f"Receipt hash mismatch: "
                        f"customer={ctx.customer_hash} vs staff={ctx.staff_hash}"
                    )
                    raise StateMachineError(
                        msg,
                        current_state=current_state,
                        event=event,
                    )
                return ExchangeState.COSIGNED

        case ExchangeState.COSIGNED:
            if event == ExchangeEvent.BEGIN_SETTLEMENT:
                return ExchangeState.SETTLEMENT_PENDING

        case ExchangeState.SETTLEMENT_PENDING:
            if event == ExchangeEvent.COMPLETE_SETTLEMENT:
                if not ctx.postings_balanced:
                    raise StateMachineError(
                        "Cannot complete settlement with unbalanced postings",
                        current_state=current_state,
                        event=event,
                    )
                return ExchangeState.SETTLED

        case ExchangeState.SETTLED:
            if event == ExchangeEvent.CLOSE_DAY:
                return ExchangeState.CLOSED

    # Fall-through for any invalid (state, event) pair
    raise StateMachineError(
        f"Illegal transition: {current_state} + {event} is undefined",
        current_state=current_state,
        event=event,
    )
