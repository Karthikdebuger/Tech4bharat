"""Domain exceptions for Gold Trust AI."""


class DomainError(Exception):
    """Base class for all domain errors."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class UnitRangeError(DomainError):
    """Raised when an integer quantity violates its valid range."""

    def __init__(self, message: str, field_name: str, value: int) -> None:
        super().__init__(message, code="UNIT_OUT_OF_RANGE")
        self.field_name = field_name
        self.value = value


class InvalidRoundingError(DomainError):
    """Raised when division rounding is called with invalid parameters."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVALID_ROUNDING_ARGUMENTS")


class StateMachineError(DomainError):
    """Raised when an illegal transition or invalid guard condition occurs."""

    def __init__(self, message: str, current_state: str, event: str) -> None:
        super().__init__(message, code="ILLEGAL_STATE_TRANSITION")
        self.current_state = current_state
        self.event = event
