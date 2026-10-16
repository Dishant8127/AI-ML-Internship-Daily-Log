#!/usr/bin/env bash
# Captures genuine testing evidence from a RUNNING server.
#
# Usage:
#   1) start the server:  .venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
#   2) run this script:   bash docs/evidence/capture_evidence.sh
#
# It writes the raw request/response captures into docs/evidence/raw/.
# Screenshots are then rendered from those raw captures by render_evidence.py.
set -u

BASE="${1:-http://127.0.0.1:8000}"
OUT="$(cd "$(dirname "$0")" && pwd)/raw"
PYTHON="$(cd "$(dirname "$0")/../.." && pwd)/.venv/Scripts/python.exe"
mkdir -p "$OUT"

capture() {
  name="$1"; shift
  {
    printf '$ curl %s\n\n' "$*"
    curl -s -i "$@"
    printf '\n'
  } > "$OUT/$name.txt" 2>&1
  echo "captured $name.txt"
}

echo "== single-request evidence =="
capture 01_health_check            "$BASE/health"
capture 02_root_endpoint           "$BASE/"
capture 03_predict_valid           -X POST "$BASE/predict" -H "Content-Type: application/json" -d '{"question":"What is a Python decorator?"}'
capture 04_chat_valid              -X POST "$BASE/api/chat" -H "Content-Type: application/json" -d '{"message":"Explain the difference between GET and POST requests.","max_new_tokens":96}'
capture 05_predict_empty_question  -X POST "$BASE/predict" -H "Content-Type: application/json" -d '{"question":""}'
capture 06_predict_whitespace      -X POST "$BASE/predict" -H "Content-Type: application/json" -d '{"question":"   "}'
capture 07_predict_missing_field   -X POST "$BASE/predict" -H "Content-Type: application/json" -d '{}'
capture 08_predict_wrong_type      -X POST "$BASE/predict" -H "Content-Type: application/json" -d '{"question":123}'
LONG=$(printf 'x%.0s' $(seq 1 4001))
capture 09_predict_too_long        -X POST "$BASE/predict" -H "Content-Type: application/json" -d "{\"question\":\"$LONG\"}"
capture 10_unknown_route           "$BASE/does-not-exist"

echo "== 20-request batch (representative questions) =="
"$PYTHON" - "$BASE" "$OUT" <<'PY'
import json, sys, time, urllib.error, urllib.request

base, out = sys.argv[1], sys.argv[2]
questions = [q.strip() for q in open(f"{out}/_questions.txt", encoding="utf-8") if q.strip()]

rows = []
for i, q in enumerate(questions, start=1):
    payload = json.dumps({"question": q}).encode("utf-8")
    req = urllib.request.Request(
        base + "/predict", data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=3600) as resp:
            code, body = resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        code, body = exc.code, {}
    dt = time.perf_counter() - t0
    rows.append({
        "n": i, "question": q, "status": code,
        "latency_sec": round(dt, 2), "answer": body.get("answer", ""),
    })
    print(f"{i:2d}  HTTP {code}  {dt:6.1f}s  {q}", flush=True)

json.dump(rows, open(f"{out}/11_batch_20_requests.json", "w", encoding="utf-8"), indent=2)
print("batch done:", len(rows), "requests")
PY

echo "all evidence captured in $OUT"
