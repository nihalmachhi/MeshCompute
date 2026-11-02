"""Immutable registry of the built-in safe task handlers."""

from meshcompute.core.errors import ConflictError
from meshcompute.handlers.base import JobHandler
from meshcompute.handlers.dataset_aggregate import DatasetAggregateHandler
from meshcompute.handlers.image_resize import ImageResizeHandler
from meshcompute.handlers.word_count import WordCountHandler

HANDLERS: dict[str, JobHandler] = {
    "word_count": WordCountHandler(),
    "image_resize": ImageResizeHandler(),
    "dataset_aggregate": DatasetAggregateHandler(),
}


def get_handler(job_type: str) -> JobHandler:
    """Return an allow-listed handler; never load code from a request."""
    try:
        return HANDLERS[job_type]
    except KeyError as exc:
        raise ConflictError(f"unsupported job type: {job_type}") from exc
