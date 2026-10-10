"""Submit a small word-count workload to a running local coordinator."""
import json
import urllib.request

payload = {
    "job_type": "word_count",
    "input_ref": "sample.txt",
    "options": {"chunk_bytes": 64},
}
request = urllib.request.Request(
    "http://localhost:8000/api/v1/jobs",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=10) as response:
    print(response.status, response.read().decode())
