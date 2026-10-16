"""Render the raw captured test output (docs/evidence/raw/) into PNG evidence images.

This does NOT invent results: every line rendered comes from a real capture produced by
capture_evidence.sh or from the notebook's recorded outputs. Missing inputs are skipped
with a warning.

Run:
    python docs/evidence/render_evidence.py
"""

import json
import os
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"

FONT_REG = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD = "C:/Windows/Fonts/consolab.ttf"
SIZE = 15
LINE_H = 21
PAD = 26
WIDTH = 1400

BG = (13, 17, 23)
FG = (230, 237, 243)
DIM = (139, 148, 158)
CYAN = (121, 192, 255)
GREEN = (63, 185, 80)
ORANGE = (210, 153, 34)
RED = (248, 81, 73)
HEAD = (88, 166, 255)


def _font(path, size=SIZE):
    return ImageFont.truetype(path, size)


def color_for(line):
    stripped = line.strip()
    if stripped.startswith("$ ") or stripped.startswith("curl"):
        return CYAN
    m = re.match(r"HTTP/\S+\s+(\d{3})", stripped)
    if m:
        code = int(m.group(1))
        if code < 300:
            return GREEN
        if code < 500:
            return ORANGE
        return RED
    if stripped.startswith("===") or stripped.startswith("###"):
        return HEAD
    if stripped.startswith("#") or stripped.startswith("//"):
        return DIM
    return FG


def render_panel(title, subtitle, lines, out_path, width=WIDTH):
    """Render a titled terminal-style panel containing `lines` of text."""
    f = _font(FONT_REG)
    fb = _font(FONT_BOLD, 19)
    fs = _font(FONT_REG, 13)

    # wrap
    wrapped = []
    max_chars = int((width - 2 * PAD) / (f.getlength("M")))
    for line in lines:
        if line == "":
            wrapped.append("")
            continue
        for part in textwrap.wrap(line, width=max_chars, subsequent_indent="    ") or [""]:
            wrapped.append(part)

    header_h = 92
    height = header_h + PAD + len(wrapped) * LINE_H + PAD
    img = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(img)

    d.text((PAD, 22), title, font=fb, fill=HEAD)
    d.text((PAD, 52), subtitle, font=fs, fill=DIM)
    d.line([(0, header_h - 8), (width, header_h - 8)], fill=(48, 54, 61))

    y = header_h + PAD
    for line in wrapped:
        d.text((PAD, y), line, font=f, fill=color_for(line))
        y += LINE_H

    img.save(out_path)
    return out_path


def read_capture(name):
    p = RAW / f"{name}.txt"
    if not p.exists():
        print("  ! missing", p.name)
        return None
    return [l.rstrip("\n") for l in p.read_text(encoding="utf-8").splitlines()]


def main():
    made = []

    def emit(fname, title, subtitle, lines):
        if lines is None:
            return
        out = HERE / fname
        render_panel(title, subtitle, lines, out)
        made.append(fname)
        print("  ->", fname)

    # 1. health check
    emit("01_health_check.png",
         "Test 1 - API health check",
         "GET /health  ::  real curl request against the running uvicorn server",
         read_capture("01_health_check"))

    # 2. successful prediction
    emit("02_prediction_success.png",
         "Test 2 - Successful prediction (request payload + generated response)",
         "POST /predict  ::  fine-tuned Qwen2.5-1.5B + LoRA",
         read_capture("03_predict_valid"))

    # 3. successful chat
    emit("03_chat_success.png",
         "Test 3 - Successful chat request",
         "POST /api/chat  ::  request payload + generated reply",
         read_capture("04_chat_valid"))

    # 4. input validation / error handling (combine all invalid cases)
    blocks = []
    for name, label in [
        ("05_predict_empty_question", "EMPTY QUESTION"),
        ("06_predict_whitespace", "WHITESPACE-ONLY QUESTION"),
        ("07_predict_missing_field", "MISSING REQUIRED FIELD"),
        ("08_predict_wrong_type", "WRONG FIELD TYPE"),
        ("09_predict_too_long", "QUESTION OVER 4000 CHARS"),
        ("10_unknown_route", "UNKNOWN ROUTE"),
    ]:
        lines = read_capture(name)
        if lines is None:
            continue
        blocks.append(f"=================== {label} ===================")
        # keep only the command line and the response status/body
        for line in lines:
            if line.startswith("$ curl"):
                blocks.append(line)
        # status line + first JSON body line
        for line in lines:
            if re.match(r"HTTP/\S+\s+\d{3}", line.strip()):
                blocks.append(line.strip())
        joined = "\n".join(lines)
        m = re.search(r"\{.*\}|\[\{.*\}\]", joined, re.S)
        if m:
            blocks.append(m.group(0).strip())
        blocks.append("")
    if blocks:
        emit("04_input_validation_errors.png",
             "Test 4 - Input validation and error handling",
             "Invalid requests :: required HTTP status codes (422 / 404)",
             blocks)

    # 5. model loading evidence
    srv = RAW / "_server.log"
    if srv.exists():
        txt = srv.read_text(encoding="utf-8", errors="replace").splitlines()
        keep = [l for l in txt if any(k in l for k in [
            "Started server", "Application startup", "Uvicorn running",
            "Loading tokenizer", "Loading base model", "Loading fine-tuned",
            "Model loaded", "Prediction completed", "Chat completed",
        ])]
        emit("05_model_loading_inference.png",
             "Test 5 - Model loading and inference evidence",
             "Adapter loaded outside the training session + per-request timing logs",
             keep)

    # 6. 20-request batch
    batch = RAW / "11_batch_20_requests.json"
    if batch.exists():
        rows = json.loads(batch.read_text(encoding="utf-8"))
        lines = [
            "Endpoint: POST /predict      Dataset: 6 held-out test + 14 representative training questions",
            "",
            f"{'#':>2}  {'HTTP':<6}{'latency':>9}  question -> generated answer",
            "-" * 150,
        ]
        for r in rows:
            ans = " ".join(r["answer"].split())
            if len(ans) > 78:
                ans = ans[:75] + "..."
            lines.append(f"{r['n']:>2}  {r['status']:<6}{r['latency_sec']:>8.1f}s  {r['question']}")
            lines.append(f"      -> {ans}")
        ok = sum(1 for r in rows if r["status"] == 200)
        avg = sum(r["latency_sec"] for r in rows) / len(rows)
        lines += ["", "-" * 150,
                  f"Requests: {len(rows)}   HTTP 200: {ok}/{len(rows)}   "
                  f"average latency: {avg:.1f}s (CPU inference, no GPU)"]
        emit("06_batch_20_requests.png",
             "Test 6 - 20 representative API requests",
             "Day 5 requirement: test at least 20 representative API requests",
             lines)

    print(f"\nRendered {len(made)} images.")
    missing = [n for n in [
        "01_health_check.png", "02_prediction_success.png", "03_chat_success.png",
        "04_input_validation_errors.png", "05_model_loading_inference.png",
        "06_batch_20_requests.png",
    ] if n not in made]
    if missing:
        print("NOT rendered (missing raw input):", ", ".join(missing))


if __name__ == "__main__":
    main()
