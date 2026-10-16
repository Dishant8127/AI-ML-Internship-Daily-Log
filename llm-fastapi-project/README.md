# AI Technical Support Assistant — LLM Fine-Tuning (LoRA) + FastAPI

Fine-tuned **Qwen2.5-1.5B-Instruct** on a small technical Q&A dataset using **LoRA**
(PEFT), and served the resulting adapter through a **FastAPI** inference API.

This repository covers the five-day project brief: dataset preparation and baseline
evaluation, LoRA fine-tuning, evaluation/comparison, and the inference API.

---

## 1. Project structure

```
llm-fastapi-project/
├── app/
│   ├── main.py            # FastAPI app: /, /health, /predict, /api/chat
│   └── llm_service.py     # Model + LoRA adapter loading and text generation
├── models/
│   └── final_adapter/     # Saved LoRA adapter (adapter_config.json, adapter_model.safetensors)
│                          #   plus the fine-tuned tokenizer and chat template
├── data/
│   ├── train.jsonl        # 28 training examples   (70%)
│   ├── validation.jsonl   #  6 validation examples (15%)
│   └── test.jsonl         #  6 held-out test examples (15%)
├── docs/evidence/         # Screenshots used as testing evidence
├── prepare_dataset.py     # Rebuilds data/*.jsonl from the source Q&A records
├── test_api.py            # End-to-end API tests (valid + invalid inputs)
├── test_results.txt       # Recorded output of test_api.py (15/15 passed)
├── Untitled8.ipynb        # Colab notebook: dataset prep, baseline, training, evaluation
├── requirements.txt       # API dependencies
└── README.md
```

The base model used is **`Qwen/Qwen2.5-1.5B-Instruct`** (Apache-2.0). Only the LoRA
adapter is stored in this repo; the base weights are downloaded automatically from the
Hugging Face Hub on first run and cached locally.

---

## 2. Setup

Requires **Python 3.10+**. From the `llm-fastapi-project` directory:

```bash
python -m venv .venv
# Windows (Git Bash):        .venv/Scripts/activate
# macOS/Linux:               source .venv/bin/activate

pip install -r requirements.txt
```

> The first launch downloads the ~3 GB base model. If you are offline, make sure it is
> already present in your Hugging Face cache.

---

## 3. Running the API

Run from inside `llm-fastapi-project` (so the `app` package is importable):

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Interactive docs are available at <http://127.0.0.1:8000/docs>.

The model is loaded lazily on the **first** `/predict` or `/api/chat` request
(~15 s on CPU). Subsequent requests reuse the loaded model.

### Endpoints

| Method | Endpoint    | Purpose                              |
|--------|-------------|--------------------------------------|
| GET    | `/`         | Basic liveness message               |
| GET    | `/health`   | Health check → `{"status": "ok"}`    |
| POST   | `/predict`  | Generate an answer (brief format)    |
| POST   | `/api/chat` | Generate a reply (chat format)       |

### `POST /predict`

Request:

```json
{ "question": "What is a Python decorator?" }
```

Response:

```json
{
  "question": "What is a Python decorator?",
  "answer": "A decorator is a function that takes another function and extends ...",
  "model": "Qwen2.5-1.5B-Instruct + LoRA"
}
```

### `POST /api/chat`

Request:

```json
{ "message": "Explain GET vs POST requests.", "max_new_tokens": 128 }
```

Response:

```json
{ "reply": "GET requests retrieve data from the server, while POST requests send data ..." }
```

---

## 4. Testing with curl

```bash
# Health check
curl http://127.0.0.1:8000/health

# Valid prediction
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a Python decorator?"}'

# Empty question -> 422
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"question": ""}'

# Whitespace-only question -> 422
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"question": "   "}'

# Missing field -> 422
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{}'
```

Or run the bundled test script (requires the server to be running):

```bash
.venv/Scripts/python.exe test_api.py
```

---

## 5. Model and training summary

| Item              | Value                                              |
|-------------------|----------------------------------------------------|
| Base model        | `Qwen/Qwen2.5-1.5B-Instruct`                      |
| Fine-tuning method| LoRA (PEFT), `r=8`, `lora_alpha=16`, dropout `0.05`|
| Target modules    | `q_proj`, `k_proj`, `v_proj`, `o_proj`             |
| Max sequence len  | 512                                                |
| Training data     | Technical Q&A dataset (see notebook)               |
| Artifact          | `models/final_adapter/`                            |

See `Untitled8.ipynb` for the full dataset preparation, baseline predictions, training
logs, held-out evaluation, and baseline-vs-fine-tuned comparison.

## 6. Known limitations

- **CPU inference is slow** (~60–100 s per ~180-token answer). A GPU is recommended for
  interactive use.
- Fine-tuning on a small dataset does not guarantee quality improvements; the notebook
  reports measured baseline-vs-fine-tuned results honestly, including cases where the
  two models agree or the fine-tuned model does not improve.
- Generation is greedy (`do_sample=False`) for reproducibility.
