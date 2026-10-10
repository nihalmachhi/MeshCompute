"""Line-aligned word-count chunks with deterministic aggregation."""
import re
from collections import Counter
from pathlib import Path
from meshcompute.common.errors import TaskExecutionError
from meshcompute.common.settings import get_settings
from meshcompute.worker.handlers.base import JsonObject

WORD_PATTERN=re.compile(r"\b[\w']+\b",re.UNICODE)
def resolve_input(input_ref: str) -> Path:
    """Resolve a shared-volume path without allowing traversal outside DATA_DIR."""
    root=get_settings().data_dir.resolve()
    normalized=input_ref.removeprefix("/data/").removeprefix("/data")
    relative=Path(normalized.lstrip("/\\"))
    path=(root/relative).resolve()
    if root not in path.parents and path!=root: raise TaskExecutionError("input_ref must stay inside the shared data directory")
    return path
class WordCountHandler:
    """Count Unicode word tokens from file chunks."""
    def split(self,input_ref: str,options: JsonObject) -> list[JsonObject]:
        """Build byte ranges aligned to newline boundaries."""
        path=resolve_input(input_ref)
        if not path.is_file(): raise TaskExecutionError(f"input file not found: {input_ref}")
        target=max(1,int(options.get("chunk_bytes",256_000)))
        chunks=[];start=0;end=0
        with path.open("rb") as source:
            while line:=source.readline():
                end+=len(line)
                if end-start>=target:
                    chunks.append({"input_ref":input_ref,"start_offset":start,"end_offset":end})
                    start=end
        if end>start: chunks.append({"input_ref":input_ref,"start_offset":start,"end_offset":end})
        return chunks
    def execute(self,payload: JsonObject) -> JsonObject:
        """Count tokens in one non-overlapping byte range."""
        path=resolve_input(str(payload["input_ref"]))
        start=int(payload["start_offset"]);end=int(payload["end_offset"])
        with path.open("rb") as source:
            source.seek(start);data=source.read(end-start)
        counts=Counter(WORD_PATTERN.findall(data.decode("utf-8")))
        return {"word_counts":dict(sorted(counts.items())),"total_words":sum(counts.values())}
    def merge(self,results: list[JsonObject]) -> JsonObject:
        """Sum partial word dictionaries into the job result."""
        counts: Counter[str]=Counter()
        for result in results:
            words=result.get("word_counts",{})
            if not isinstance(words,dict): raise TaskExecutionError("word count result is malformed")
            counts.update({str(word):int(count) for word,count in words.items()})
        return {"total_words":sum(counts.values()),"unique_words":len(counts),"word_counts":dict(sorted(counts.items()))}
