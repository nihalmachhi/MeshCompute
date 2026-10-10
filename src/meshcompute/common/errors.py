"""Domain exceptions translated to stable HTTP errors at the API boundary."""
class MeshComputeError(Exception):
    """Base class for expected service errors."""
class NotFoundError(MeshComputeError):
    """Requested domain object does not exist."""
class ConflictError(MeshComputeError):
    """Request conflicts with current state or fencing token."""
class BackpressureError(MeshComputeError):
    """Queue capacity has been reached."""
class InvalidTransitionError(MeshComputeError):
    """Requested state transition is not allowed."""
class TaskExecutionError(MeshComputeError):
    """A registered worker handler failed or timed out."""
