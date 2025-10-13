"""Custom exceptions for Dprod."""


class DprodException(Exception):
    """Base exception for all Dprod errors."""
    pass


class AuthenticationError(DprodException):
    """Authentication related errors."""
    pass


class ProjectDetectionError(DprodException):
    """Project type detection failed."""
    pass


class BuildError(DprodException):
    """Build process failed."""
    pass


class ContainerError(DprodException):
    """Container runtime error."""
    pass


class ResourceLimitError(DprodException):
    """Resource limits exceeded."""
    pass


class ValidationError(DprodException):
    """Input validation error."""
    pass


class NotFoundError(DprodException):
    """Resource not found."""
    pass


class DeploymentError(DprodException):
    """Deployment process error."""
    pass
