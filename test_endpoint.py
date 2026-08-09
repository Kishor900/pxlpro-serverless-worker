"""Test the MiniMax H3 serverless endpoint from a local PC.

Usage:
  set RUNPOD_API_KEY=rpa_xxx        (your RunPod API key)
  set ENDPOINT_ID=xxxxxxxx          (from the endpoint page)
  python test_endpoint.py workflow_api.json
"""
import base64
import json
import os
import sys
import time
import urllib.request

API_KEY = os.environ.get("RUNPOD_API_KEY")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
WORKFLOW_FILE = sys.argv[1] if len(sys.argv) > 1 else "workflow_api.json"

if not API_KEY or not ENDPOINT_ID:
    sys.exit("Set RUNPOD_API_KEY and ENDPOINT_ID environment variables first.")

BASE = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"
HDRS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def call(method, url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 method=method, headers=HDRS)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


workflow = json.load(open(WORKFLOW_FILE, encoding="utf-8"))
print(f"Submitting job to endpoint {ENDPOINT_ID} ...")
job = call("POST", f"{BASE}/run", {"input": {"workflow": workflow}})
job_id = job["id"]
print(f"Job {job_id} queued. Polling (cold start + generation can take several minutes)...")

t0 = time.time()
while True:
    time.sleep(10)
    status = call("GET", f"{BASE}/status/{job_id}")
    state = status.get("status")
    print(f"  [{int(time.time()-t0):>4}s] {state}")
    if state in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
        break

if state != "COMPLETED":
    print(json.dumps(status, indent=2)[:3000])
    sys.exit(f"Job ended: {state}")

# Save any base64 payloads in the output; print everything else.
out = status.get("output", {})
saved = []
items = out.get("images", []) if isinstance(out, dict) else []
for i, item in enumerate(items):
    data = item.get("data")
    if not data:
        print("Non-inline output item:", json.dumps(item)[:500])
        continue
    name = item.get("filename", f"output_{i}.bin")
    with open(name, "wb") as f:
        f.write(base64.b64decode(data))
    saved.append(name)

print(f"\nDone in {int(time.time()-t0)}s.")
if saved:
    print("Saved:", *saved)
else:
    print("Raw output:", json.dumps(out, indent=2)[:3000])
