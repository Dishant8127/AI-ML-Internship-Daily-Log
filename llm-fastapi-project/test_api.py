"""End-to-end API tests for the fine-tuned Qwen2.5 LoRA inference server.

Start the server first, then run:

    .venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
    .venv/Scripts/python.exe test_api.py

The valid-prediction tests trigger model loading and CPU generation, so they can take
a couple of minutes to complete.
"""

import json
import sys
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
TIMEOUT = 600


def call(method, path, payload=None):
    url = BASE_URL + path
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"raw": body}


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  -> {detail}" if detail else ""), flush=True)
    return condition


def main():
    results = []

    # --- health / liveness -------------------------------------------------
    code, body = call("GET", "/health")
    results.append(check("/health returns 200", code == 200, str(body)))
    results.append(check("/health status ok", body.get("status") == "ok", str(body)))

    code, body = call("GET", "/")
    results.append(check("/ returns 200", code == 200, str(body)))

    # --- valid predictions -------------------------------------------------
    code, body = call("POST", "/predict", {"question": "What is a Python decorator?"})
    results.append(check("/predict valid returns 200", code == 200, str(code)))
    results.append(
        check(
            "/predict response shape",
            isinstance(body.get("answer"), str)
            and body.get("question") == "What is a Python decorator?"
            and "model" in body,
            str(list(body.keys())),
        )
    )
    results.append(check("/predict answer non-empty", bool(body.get("answer", "").strip())))
    print("     answer:", body.get("answer", ""), flush=True)

    code, body = call("POST", "/api/chat", {"message": "Explain GET vs POST.", "max_new_tokens": 64})
    results.append(check("/api/chat valid returns 200", code == 200, str(code)))
    results.append(check("/api/chat reply non-empty", bool(body.get("reply", "").strip())))

    # --- invalid inputs ----------------------------------------------------
    code, _ = call("POST", "/predict", {"question": ""})
    results.append(check("/predict empty question -> 422", code == 422, str(code)))

    code, _ = call("POST", "/predict", {"question": "   "})
    results.append(check("/predict whitespace question -> 422", code == 422, str(code)))

    code, _ = call("POST", "/predict", {})
    results.append(check("/predict missing field -> 422", code == 422, str(code)))

    code, _ = call("POST", "/predict", {"question": "x" * 4001})
    results.append(check("/predict over-long question -> 422", code == 422, str(code)))

    code, _ = call("POST", "/predict", {"question": 123})
    results.append(check("/predict wrong type -> 422", code == 422, str(code)))

    code, _ = call("POST", "/api/chat", {"message": ""})
    results.append(check("/api/chat empty message -> 422", code == 422, str(code)))

    # --- unknown route -----------------------------------------------------
    code, _ = call("GET", "/does-not-exist")
    results.append(check("/unknown route -> 404", code == 404, str(code)))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
