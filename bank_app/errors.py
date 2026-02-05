class ServiceError(Exception):
    """Base class for service layer errors."""


class ValidationError(ServiceError):
    """Raised when inputs fail validation."""


class AuthError(ServiceError):
    """Raised when authentication fails."""


class NotFoundError(ServiceError):
    """Raised when an entity does not exist."""


class ConflictError(ServiceError):
    """Raised when a unique constraint would be violated."""


class BusinessRuleError(ServiceError):
    """Raised when a business rule is violated."""
