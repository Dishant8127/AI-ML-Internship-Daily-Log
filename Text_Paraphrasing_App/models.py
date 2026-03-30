from transformers import pipeline

paraphrase_pipeline = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

def paraphrase_text(text, tone="neutral"):

    if tone == "formal":
        prompt = f"""
Paraphrase the sentence in a highly formal and professional tone.
Keep the exact same meaning and tense. Do NOT change meaning.

Sentence: {text}

Paraphrased:
"""
    elif tone == "simple":
        prompt = f"""
Paraphrase the sentence in a very simple and easy way.
Keep the same meaning.

Sentence: {text}

Paraphrased:
"""
    elif tone == "academic":
        prompt = f"""
Paraphrase the sentence in an academic and scholarly style.
Keep the same meaning and tone consistency.

Sentence: {text}

Paraphrased:
"""
    else:
        prompt = f"""
Paraphrase the sentence using different words while keeping the same meaning.

Sentence: {text}

Paraphrased:
"""

    results = paraphrase_pipeline(
        prompt,
        max_length=100,
        do_sample=True,
        temperature=1.0,
        top_p=0.9,
        repetition_penalty=1.2,
        num_return_sequences=3
    )

    outputs = []
    for r in results:
        out = r["generated_text"]
        if "Paraphrased:" in out:
            out = out.split("Paraphrased:")[-1].strip()
        outputs.append(out)

    best_output = None
    for out in outputs:
        if "will " not in out.lower():
            best_output = out
            break

    if not best_output:
        best_output = outputs[0]

    return best_output