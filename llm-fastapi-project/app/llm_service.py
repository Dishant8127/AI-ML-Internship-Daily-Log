
import os
import threading

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
MODEL_LABEL = "Qwen2.5-1.5B-Instruct + LoRA"
ADAPTER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "final_adapter")
)

tokenizer = None
model = None

# Guards lazy loading so concurrent requests cannot load the model twice.
_load_lock = threading.Lock()


def load_model():
    global tokenizer, model

    if model is not None:
        return tokenizer, model

    with _load_lock:
        # Another thread may have finished loading while we waited for the lock.
        if model is not None:
            return tokenizer, model

        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            ADAPTER_PATH,
            local_files_only=True
        )

        print("Loading base model on CPU...")
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            dtype=torch.float32,
            low_cpu_mem_usage=True,
        )

        print("Loading fine-tuned LoRA adapter...")
        model = PeftModel.from_pretrained(
            base_model,
            ADAPTER_PATH,
            is_trainable=False,
        )

        model.eval()
        print("Model loaded successfully.")

        return tokenizer, model



def generate_response(message: str, max_new_tokens: int = 128) -> str:
    tokenizer, model = load_model()

    messages = [
        {
            "role": "user",
            "content": message,
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    )

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    input_length = inputs["input_ids"].shape[-1]
    new_tokens = outputs[0][input_length:]
    answer = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return answer.strip()
