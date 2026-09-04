class KernelError(Exception):
    """Base class for ANKA Game Kernel errors."""


class DuplicateDefinitionError(KernelError):
    """Raised when a registry receives the same canonical identifier twice."""


class DefinitionNotFoundError(KernelError, KeyError):
    """Raised when a required canonical definition is absent."""
