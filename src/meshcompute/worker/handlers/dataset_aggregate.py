"""CSV numeric-column aggregation with row-range chunking."""
import csv
from meshcompute.common.errors import TaskExecutionError
from meshcompute.worker.handlers.word_count import resolve_input
from meshcompute.worker.handlers.base import JsonObject

class DatasetAggregateHandler:
    """Compute mergeable count, sum, minimum, and maximum statistics."""
    def split(self,input_ref: str,options: JsonObject) -> list[JsonObject]:
        """Create stable ranges over data rows after the CSV header."""
        path=resolve_input(input_ref)
        if not path.is_file(): raise TaskExecutionError(f"CSV file not found: {input_ref}")
        chunk_size=max(1,int(options.get("rows_per_task",500)))
        with path.open("r",encoding="utf-8",newline="") as source:
            reader=csv.reader(source);header=next(reader,None)
            if not header: raise TaskExecutionError("CSV must include a header and data")
            row_count=sum(1 for _ in reader)
        column=str(options.get("value_column",header[0]))
        if column not in header: raise TaskExecutionError(f"numeric column {column!r} is absent")
        return [{"input_ref":input_ref,"row_start":start,"row_end":min(start+chunk_size,row_count),"value_column":column}
                for start in range(0,row_count,chunk_size)]
    def execute(self,payload: JsonObject) -> JsonObject:
        """Read and aggregate a half-open row range from a CSV."""
        path=resolve_input(str(payload["input_ref"]));start=int(payload["row_start"]);end=int(payload["row_end"])
        column=str(payload["value_column"]);values=[]
        with path.open("r",encoding="utf-8",newline="") as source:
            reader=csv.DictReader(source)
            for index,row in enumerate(reader):
                if index<start: continue
                if index>=end: break
                try: values.append(float(row[column]))
                except (KeyError,TypeError,ValueError) as exc: raise TaskExecutionError(f"invalid numeric value at CSV row {index+2}") from exc
        return {"count":len(values),"sum":sum(values),"min":min(values) if values else None,"max":max(values) if values else None}
    def merge(self,results: list[JsonObject]) -> JsonObject:
        """Combine partial statistics without loading input files again."""
        count=sum(int(item["count"]) for item in results);total=sum(float(item["sum"]) for item in results)
        mins=[float(item["min"]) for item in results if item.get("min") is not None]
        maxs=[float(item["max"]) for item in results if item.get("max") is not None]
        return {"count":count,"sum":total,"mean":total/count if count else None,"min":min(mins) if mins else None,"max":max(maxs) if maxs else None}
