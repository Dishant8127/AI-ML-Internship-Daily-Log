"""Render evidence images from the notebook's RECORDED outputs.

IMPORTANT: everything rendered here is transcribed from the saved cell outputs of
``Untitled8.ipynb`` (the Google Colab run). It is NOT regenerated here, and the training
run is not repeated. The loss curve is the actual PNG stored in the notebook output.

Run:
    python docs/evidence/render_notebook_evidence.py
"""

import base64
import json
from pathlib import Path

from render_evidence import render_panel

HERE = Path(__file__).resolve().parent
NB_PATH = HERE.parent.parent / "Untitled8.ipynb"

NB = json.loads(NB_PATH.read_text(encoding="utf-8"))
CELLS = NB["cells"]


def text_of(idx):
    out = []
    for o in CELLS[idx].get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif o.get("output_type") in ("execute_result", "display_data"):
            d = o.get("data", {})
            if "text/plain" in d:
                out.append("".join(d["text/plain"]))
    return "\n".join(out).strip()


def source_of(idx):
    return "".join(CELLS[idx]["source"])


def main():
    print("Rendering notebook-derived evidence...")

    # 07 - sample predictions from both models (cell 33 prints all 6 held-out questions)
    samples = [l for l in text_of(33).splitlines() if l.strip() != ""]
    if samples:
        render_panel(
            "Evaluation - sample predictions: original vs fine-tuned",
            "Transcribed from Untitled8.ipynb cell 33 (recorded Colab outputs) - 6 held-out test questions",
            ["The 6 questions below are the held-out test set (data/test.jsonl).",
             "\"ORIGINAL MODEL\" = Qwen2.5-1.5B-Instruct, \"FINE-TUNED MODEL\" = + LoRA adapter.",
             ""] + samples,
            HERE / "07_baseline_vs_finetuned_samples.png",
        )
        print("  -> 07_baseline_vs_finetuned_samples.png")

    # 08 - training loss curve (real image stored in the notebook output)
    for cell in CELLS:
        for o in cell.get("outputs", []):
            d = o.get("data", {})
            if "image/png" in d:
                raw = d["image/png"]
                if isinstance(raw, list):
                    raw = "".join(raw)
                (HERE / "08_training_loss_curve.png").write_bytes(base64.b64decode(raw))
                print("  -> 08_training_loss_curve.png")
                break
        else:
            continue
        break

    # 09 - training + validation metrics (cells 20 and 22)
    lines = [
        "--- Recorded training summary (Untitled8.ipynb cell 20) ---",
        text_of(20),
        "",
        "--- Recorded training log tail (Untitled8.ipynb cell 22) ---",
        text_of(22),
    ]
    render_panel(
        "Training and validation metrics (recorded)",
        "Transcribed from Untitled8.ipynb recorded outputs - LoRA r=8, alpha=16, 3 epochs, GPU (Colab)",
        lines,
        HERE / "09_training_and_eval_metrics.png",
    )
    print("  -> 09_training_and_eval_metrics.png")

    # 10 - evaluation summary: latency / memory / comparison (cells 32, 42, 46)
    lines = [
        "--- Held-out evaluation on 6 test questions (cell 32) ---",
        text_of(32),
        "",
        "--- Corrected 50-question comparison (cell 42) ---",
        text_of(42),
        "",
        "--- Summary metrics written by the notebook (cell 46) ---",
        text_of(46),
    ]
    render_panel(
        "Evaluation metrics: latency, memory, comparison (recorded)",
        "Transcribed from Untitled8.ipynb recorded outputs - measured on Google Colab GPU",
        lines,
        HERE / "10_evaluation_summary.png",
    )
    print("  -> 10_evaluation_summary.png")


if __name__ == "__main__":
    main()
