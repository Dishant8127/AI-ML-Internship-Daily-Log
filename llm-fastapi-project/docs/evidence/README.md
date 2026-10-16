# Testing evidence

All images in this folder come from **real runs**. Nothing here was mocked, hand-edited, or
invented. Two kinds of source are used, and each file states which:

- **Live API captures** — produced by `capture_evidence.sh` against a running
  `uvicorn app.main:app` server. The raw request/response bytes are kept in `raw/`.
- **Recorded notebook outputs** — transcribed from the saved cell outputs of
  `Untitled8.ipynb` (the Google Colab run). The training was **not** rerun here.

---

## Screenshots

| # | File | What it demonstrates | How it was captured |
|---|------|----------------------|---------------------|
| 1 | `01_health_check.png` | `GET /health` returns `HTTP 200` with `{"status":"ok"}` | Live `curl -i` capture (`raw/01_health_check.txt`) |
| 2 | `02_prediction_success.png` | `POST /predict` with a request payload returns `HTTP 200` and a real generated answer + `model` field | Live `curl -i` capture (`raw/03_predict_valid.txt`) |
| 3 | `03_chat_success.png` | `POST /api/chat` returns `HTTP 200` with a generated reply | Live `curl -i` capture (`raw/04_chat_valid.txt`) |
| 4 | `04_input_validation_errors.png` | Input validation / error handling: empty question, whitespace-only, missing field, wrong type, >4000 chars → `HTTP 422`; unknown route → `HTTP 404` | Live `curl -i` captures (`raw/05…10_*.txt`) |
| 5 | `05_model_loading_inference.png` | The adapter loads **outside the training session** ("Loading tokenizer / base model / fine-tuned LoRA adapter / Model loaded successfully") plus per-request response-time log lines | uvicorn server log (`raw/_server.log`) |
| 6 | `06_batch_20_requests.png` | 20 representative API requests through `POST /predict` — all `HTTP 200`, question → generated answer, latency per request | Batch capture (`raw/11_batch_20_requests.json`) |
| 7 | `07_baseline_vs_finetuned_samples.png` | Sample predictions from **both** models on the 6 held-out test questions (reference / original / fine-tuned) | Transcribed from notebook cell 33 (recorded output) |
| 8 | `08_training_loss_curve.png` | Training loss curve produced during fine-tuning | The actual PNG stored in the notebook's cell output (extracted unchanged) |
| 9 | `09_training_and_eval_metrics.png` | Final training loss `1.1349`, `eval_loss` `0.7977`, peak GPU memory `3.04 GB`, and the training-log tail | Transcribed from notebook cells 20 and 22 (recorded output) |
| 10 | `10_evaluation_summary.png` | Latency and memory on the held-out set, plus the 50-question corrected comparison summary | Transcribed from notebook cells 32, 42 and 46 (recorded output) |
| 11 | `api_docs.png` | Live screenshot of the running server's Swagger UI showing the `GET` and `POST` endpoint definitions | Headless Chrome screenshot of `http://127.0.0.1:8000/docs` while uvicorn was running |
| 12 | `api_test_results.png` | Summary of the automated end-to-end suite (`test_api.py`): 15/15 checks passed | Rendered from the real `test_results.txt` output |

---

## How to reproduce

```bash
# 1. start the server
.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000

# 2. capture live evidence (writes docs/evidence/raw/, ~35 min on CPU)
bash docs/evidence/capture_evidence.sh

# 3. render the screenshots
python docs/evidence/render_evidence.py            # images 1-6
python docs/evidence/render_notebook_evidence.py   # images 7-10
```

Note: `render_evidence.py` / `render_notebook_evidence.py` need Pillow (`pip install pillow`).
The API itself does not depend on Pillow.

---

## Honest notes

- The `$ curl ...` lines in the captures show the arguments without quotes (an artifact of the
  capture echo). The commands were executed with proper quoting; the raw responses are byte-accurate.
- Latency values (average ~77 s per answer) are **CPU** numbers. The notebook's ~1.1–1.2 s figures
  are **GPU** (Colab) numbers. They are not comparable.
- Images 7–10 are transcriptions of the notebook's recorded outputs; they are evidence of what the
  Colab run produced, not of a re-run performed here.

## Evidence the PDF asks for that is NOT available in the project

- **ROUGE-L and exact-match scores** — not computed anywhere in the notebook.
- **Failure-case analysis (≥5 cases)** — the notebook references
  `day3_failure_case_candidates.csv`, but no content for it exists in the repo or notebook outputs.
- **Human rubric scores** — the notebook's own summary reports
  `"manual_rubric_scoring_complete": false`.
- **Recorded demonstration / walkthrough** — none exists.
