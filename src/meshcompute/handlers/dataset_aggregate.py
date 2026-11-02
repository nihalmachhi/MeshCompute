"""CSV numeric-column aggregation with record-aware byte-range chunks."""

import csv
import io
from collections.abc import Iterator

from meshcompute.core.errors import TaskExecutionError
from meshcompute.handlers.base import JsonObject
from meshcompute.handlers.word_count import resolve_input


def _csv_records(source) -> Iterator[tuple[int, int, bytes]]:
    """Yield logical CSV records and their half-open byte offsets.
    Newlines inside quoted fields stay within the record. The scanner stores at
    most one logical record at a time, so it does not load the full dataset.
    """
    start = 0
    offset = 0
    quoted = False
    record = bytearray()
    for physical_line in source:
        record.extend(physical_line)
        offset += len(physical_line)
        if physical_line.count(b'"') % 2:
            quoted = not quoted
        if not quoted:
            yield start, offset, bytes(record)
            start = offset
            record.clear()
    if quoted:
        raise TaskExecutionError("CSV ends inside a quoted field")
    if record:
        yield start, offset, bytes(record)


class DatasetAggregateHandler:
    """Compute mergeable count, sum, minimum, and maximum statistics."""

    def split(self, input_ref: str, options: JsonObject) -> list[JsonObject]:
        """Scan CSV records once and create chunks addressable by byte range."""
        path = resolve_input(input_ref)
        if not path.is_file():
            raise TaskExecutionError(f"CSV file not found: {input_ref}")
        chunk_size = int(options.get("rows_per_task", 500))
        if chunk_size < 1:
            raise TaskExecutionError("rows_per_task must be positive")
        try:
            records = _csv_records(path.open("rb"))
            header_record = next(records, None)
            if header_record is None:
                raise TaskExecutionError("CSV must include a header and data")
            header_start, header_end, raw_header = header_record
            if header_start != 0:
                raise TaskExecutionError("CSV header must start at byte zero")
            header = next(csv.reader(io.StringIO(raw_header.decode("utf-8-sig"))))
            if not header:
                raise TaskExecutionError("CSV must include a header and data")
            column = str(options.get("value_column", header[0]))
            if column not in header:
                raise TaskExecutionError(f"numeric column {column!r} is absent")
            chunks = []
            chunk_start = header_end
            rows_in_chunk = 0
            row_index = 0
            for _start, record_end, raw_record in records:
                parsed = next(csv.reader(io.StringIO(raw_record.decode("utf-8-sig"))), [])
                if not parsed:
                    continue
                rows_in_chunk += 1
                row_index += 1
                if rows_in_chunk >= chunk_size:
                    chunks.append(
                        {
                            "input_ref": input_ref,
                            "byte_start": chunk_start,
                            "byte_end": record_end,
                            "header": header,
                            "value_column": column,
                            "row_start": row_index - rows_in_chunk,
                            "row_end": row_index,
                        }
                    )
                    chunk_start = record_end
                    rows_in_chunk = 0
            if rows_in_chunk:
                chunks.append(
                    {
                        "input_ref": input_ref,
                        "byte_start": chunk_start,
                        "byte_end": path.stat().st_size,
                        "header": header,
                        "value_column": column,
                        "row_start": row_index - rows_in_chunk,
                        "row_end": row_index,
                    }
                )
        except (UnicodeDecodeError, csv.Error) as exc:
            raise TaskExecutionError("invalid UTF-8 CSV input") from exc
        if not chunks:
            raise TaskExecutionError("CSV must include a header and data")
        return chunks

    def execute(self, payload: JsonObject) -> JsonObject:
        """Read only the assigned byte range and aggregate its numeric values."""
        path = resolve_input(str(payload["input_ref"]))
        byte_start = int(payload["byte_start"])
        byte_end = int(payload["byte_end"])
        if byte_start < 0 or byte_end < byte_start or byte_end > path.stat().st_size:
            raise TaskExecutionError("CSV chunk byte range is invalid")
        with path.open("rb") as source:
            source.seek(byte_start)
            contents = source.read(byte_end - byte_start).decode("utf-8-sig")
        header = [str(name) for name in payload["header"]]
        column = str(payload["value_column"])
        values = []
        try:
            for row in csv.DictReader(io.StringIO(contents), fieldnames=header):
                if not row or all(value is None for value in row.values()):
                    continue
                try:
                    values.append(float(row[column]))
                except (KeyError, TypeError, ValueError) as exc:
                    chunk_range = f"{payload['row_start']}:{payload['row_end']}"
                    raise TaskExecutionError(
                        f"invalid numeric value in CSV chunk {chunk_range}"
                    ) from exc
        except csv.Error as exc:
            raise TaskExecutionError("invalid CSV chunk") from exc
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
        }

    def merge(self, results: list[JsonObject]) -> JsonObject:
        """Combine partial statistics without rereading the original CSV."""
        count = sum(int(item["count"]) for item in results)
        total = sum(float(item["sum"]) for item in results)
        mins = [float(item["min"]) for item in results if item.get("min") is not None]
        maxs = [float(item["max"]) for item in results if item.get("max") is not None]
        return {
            "count": count,
            "sum": total,
            "mean": total / count if count else None,
            "min": min(mins) if mins else None,
            "max": max(maxs) if maxs else None,
        }
