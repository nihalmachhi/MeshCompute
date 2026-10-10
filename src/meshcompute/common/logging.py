"""Minimal structured JSON logging without payload or secret logging."""
import json
import logging
from datetime import datetime,timezone

class JsonFormatter(logging.Formatter):
    """Format records as compact JSON with UTC timestamps."""
    def format(self,record: logging.LogRecord) -> str:
        """Serialize safe standard fields and explicit context values."""
        payload={"timestamp":datetime.now(timezone.utc).isoformat(),"level":record.levelname,
                 "logger":record.name,"message":record.getMessage()}
        for key in ("job_id","task_id","worker_id","event"):
            value=getattr(record,key,None)
            if value is not None: payload[key]=str(value)
        if record.exc_info: payload["exception"]=self.formatException(record.exc_info)
        return json.dumps(payload,ensure_ascii=True)

def configure_logging(level: str) -> None:
    """Configure the root logger once for consistent service logs."""
    handler=logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root=logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
