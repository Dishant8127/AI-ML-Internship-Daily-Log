
# Tokenization Report

## Tokenizer Comparison

| Tokenizer   |   Dynamic Speed (s) |   Fixed Speed (s) |   Avg Length |   % Truncated |
|:------------|--------------------:|------------------:|-------------:|--------------:|
| bert        |                6.98 |              8.6  |        23.67 |             0 |
| distilbert  |                7.19 |              8.93 |        23.67 |             0 |
| roberta     |                8.93 |              4.93 |        29.7  |             0 |

---

## Recommended Tokenizer

Recommended tokenizer: **DistilBERT**

### Reason:
- Faster tokenization
- Lower memory usage
- Good balance between speed and accuracy
- Suitable for finetuning on medium datasets

---

## Best max_length

Recommended max_length: **128**

### Justification:
- Most sequences are below 128 tokens
- Reduces memory usage
- Faster training
- Minimal truncation percentage

---

## Dynamic vs Fixed Padding

### Dynamic Padding
- Saves memory
- Efficient for varying sequence sizes
- Better during training with DataCollator

### Fixed Padding
- Faster batch processing
- Better GPU utilization
- Easier tensor handling

---

## Histogram Screenshots

Saved inside tokenized folder.
