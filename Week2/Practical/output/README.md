---
language:
  - en
license: apache-2.0
task_categories:
  - text-generation
  - question-answering
task_ids:
  - instruction-tuning
tags:
  - instruction-tuning
  - alpaca
  - sharegpt
  - chatml
  - llm
  - fine-tuning
size_categories:
  - 1K<n<10K
source_datasets:
  - databricks/databricks-dolly-15k
  - Open Trivia Database API
  - JSONPlaceholder API
pretty_name: Intern Instruction Dataset
dataset_info:
  features:
    - name: id
      dtype: string
    - name: source
      dtype: string
    - name: category
      dtype: string
    - name: difficulty
      dtype: string
    - name: instruction
      dtype: string
    - name: input
      dtype: string
    - name: output
      dtype: string
    - name: quality_score
      dtype: float64
  splits:
    - name: train
      num_examples: 737
    - name: validation
      num_examples: 92
    - name: test
      num_examples: 93
---

# Intern Instruction Dataset

A curated instruction-following dataset assembled from multiple public sources
as part of an AI/ML internship pipeline. The dataset covers general knowledge,
open-domain QA, and summarization tasks.

## Dataset Details

**Date created:** 2026-04-12  
**Total samples:** 922  
**Languages:** English  
**License:** Apache 2.0

## Data Sources

| Source | Samples | Description |
|---|---|---|
| Open Trivia DB API | ~300 | General knowledge multiple-choice questions |
| Databricks Dolly 15k | ~700 | Open-source instruction-following samples |
| JSONPlaceholder API | ~100 | Synthetic summarization pairs |

## Dataset Structure

```json
{
  "id": "sample_00001",
  "source": "dolly_15k",
  "category": "open_qa",
  "difficulty": "unknown",
  "instruction": "What is the capital of France?",
  "input": "",
  "output": "The capital of France is Paris.",
  "quality_score": 0.6
}
```

## Splits

| Split | Samples |
|---|---|
| train | 737 |
| validation | 92 |
| test | 93 |

## Instruction Formats

This dataset is also available in three fine-tuning formats (see repository files):

- `alpaca_format.json` - Stanford Alpaca flat JSON format
- `sharegpt_format.json` - ShareGPT conversation format
- `chatml_format.json` - OpenAI ChatML message format

## Cleaning Pipeline

1. Schema validation
2. Null removal and empty string filtering
3. Length filtering (min 10 chars instruction, 1-2048 words output)
4. MD5 deduplication on instruction text
5. Heuristic quality scoring (threshold 0.0)

## Usage

```python
from datasets import load_dataset

dataset = load_dataset('YOUR_USERNAME/intern-instruction-dataset')
train_data = dataset['train']
print(train_data[0])
```

## Citation

If using Dolly 15k samples, cite the original dataset:

```bibtex
@misc{dolly,
  author = {Conover, Mike and others},
  title  = {Free Dolly: Introducing the World's First Truly Open Instruction-Tuned LLM},
  year   = {2023},
  url    = {https://www.databricks.com/blog/2023/04/12/dolly-first-open-commercially-viable-instruction-tuned-llm}
}
```
