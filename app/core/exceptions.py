from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DuplicateEventError(AppException):
    """Raised when attempting to process a duplicate event."""

    def __init__(self, event_id: str, processed_at: str) -> None:
        super().__init__(
            code="DUPLICATE_EVENT",
            message=f"Event {event_id} has already been processed",
            details={"event_id": event_id, "processed_at": processed_at},
        )


class InvalidEventTypeError(AppException):
    """Raised when an unknown event type is received."""

    def __init__(self, event_type: str) -> None:
        super().__init__(
            code="INVALID_EVENT_TYPE",
            message=f"Unknown event type: {event_type}",
            details={"event_type": event_type},
        )


class InvalidCurrencyError(AppException):
    """Raised when an invalid currency is provided."""

    def __init__(self, currency: str) -> None:
        super().__init__(
            code="INVALID_CURRENCY",
            message=f"Invalid currency: {currency}",
            details={"currency": currency},
        )


class InvalidAmountError(AppException):
    """Raised when an invalid amount is provided."""

    def __init__(self, amount: int, reason: str = "") -> None:
        super().__init__(
            code="INVALID_AMOUNT",
            message=f"Invalid amount: {amount}. {reason}",
            details={"amount": amount, "reason": reason},
        )


class RestaurantNotFoundError(AppException):
    """Raised when a restaurant is not found."""

    def __init__(self, restaurant_id: str) -> None:
        super().__init__(
            code="RESTAURANT_NOT_FOUND",
            message=f"Restaurant {restaurant_id} not found",
            details={"restaurant_id": restaurant_id},
        )


class PayoutNotFoundError(AppException):
    """Raised when a payout is not found."""

    def __init__(self, payout_id: str) -> None:
        super().__init__(
            code="PAYOUT_NOT_FOUND",
            message=f"Payout {payout_id} not found",
            details={"payout_id": payout_id},
        )


class PayoutGenerationError(AppException):
    """Raised when payout generation fails."""

    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="PAYOUT_GENERATION_FAILED",
            message=f"Payout generation failed: {reason}",
            details=details or {},
        )
