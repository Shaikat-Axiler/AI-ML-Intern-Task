#!/usr/bin/env python3
"""
llm_compare.py — CLI tool to compare inference across multiple models.

Usage:
    python llm_compare.py "Your prompt here" [options]

Options:
    --models       Space-separated list: ollama gpt2 distilgpt2 (default: all)
    --temperature  Float 0.0-2.0  (default: 0.7)
    --top_p        Float 0.0-1.0  (default: 0.9)
    --top_k        Int            (default: 50)
    --max_tokens   Int            (default: 80)
    --ollama_model Ollama model name (default: llama3.1)
    --output       Path to save results (optional)
"""

import argparse
import time
import textwrap


# ─── Ollama backend ───────────────────────────────────────────────────────────

def run_ollama(prompt, model="llama3.1", temperature=0.7,
               top_p=0.9, top_k=50, max_tokens=80):
    try:
        import requests
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_tokens,
            }
        }
        r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["response"].strip()
    except Exception as e:
        return f"[Ollama error: {e}]"


# ─── Hugging Face backend ─────────────────────────────────────────────────────

def run_hf_model(prompt, model_name="gpt2", temperature=0.7,
                 top_p=0.9, top_k=50, max_tokens=80):
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        model.eval()

        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )

        new_ids = out[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(new_ids, skip_special_tokens=True).strip()
    except Exception as e:
        return f"[HF error: {e}]"


# ─── Dispatcher ───────────────────────────────────────────────────────────────

BACKENDS = {
    "ollama": ("Ollama (llama3.1)", lambda p, a: run_ollama(
        p, a.ollama_model, a.temperature, a.top_p, a.top_k, a.max_tokens
    )),
    "gpt2": ("GPT-2 (124M)", lambda p, a: run_hf_model(
        p, "gpt2", a.temperature, a.top_p, a.top_k, a.max_tokens
    )),
    "distilgpt2": ("DistilGPT-2 (82M)", lambda p, a: run_hf_model(
        p, "distilgpt2", a.temperature, a.top_p, a.top_k, a.max_tokens
    )),
}


# ─── Display helpers ──────────────────────────────────────────────────────────

def box(title, text, width=72):
    border = "─" * (width - 2)
    lines = textwrap.wrap(text, width - 4) if text else ["(no output)"]
    body = "\n".join(f"│  {l:<{width-4}}  │" for l in lines)
    return (
        f"┌{border}┐\n"
        f"│  {title:<{width-4}}  │\n"
        f"├{border}┤\n"
        f"{body}\n"
        f"└{border}┘"
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compare LLM outputs across multiple models."
    )
    parser.add_argument("prompt", type=str, help="Input prompt")
    parser.add_argument("--models", nargs="+", default=list(BACKENDS.keys()),
                        choices=list(BACKENDS.keys()), help="Models to compare")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--top_k", type=int, default=50)
    parser.add_argument("--max_tokens", type=int, default=80)
    parser.add_argument("--ollama_model", type=str, default="llama3.1")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    separator = "═" * 72
    output_lines = []

    header = [
        separator,
        " LLM INFERENCE COMPARISON",
        separator,
        f" Prompt      : {args.prompt}",
        f" Models      : {args.models}",
        f" temperature={args.temperature}  top_p={args.top_p}  top_k={args.top_k}  max_tokens={args.max_tokens}",
        separator,
    ]
    for line in header:
        print(line)
        output_lines.append(line)

    results_summary = []

    for key in args.models:
        display_name, runner = BACKENDS[key]
        print(f"\nRunning {display_name}...", end=" ", flush=True)

        t0 = time.time()
        result = runner(args.prompt, args)
        elapsed = time.time() - t0

        print(f"done ({elapsed:.1f}s)")

        title = f"{display_name}  [{elapsed:.1f}s]"
        b = box(title, result)
        print(b)
        output_lines.append(b)
        results_summary.append((display_name, elapsed, len(result.split())))

    # Summary table
    print(f"\n{separator}")
    print(" SUMMARY")
    print(separator)
    print(f" {'Model':<25} {'Latency':>10} {'Words':>8}")
    print(f" {'─'*25} {'─'*10} {'─'*8}")
    for name, lat, words in results_summary:
        print(f" {name:<25} {lat:>9.1f}s {words:>8}")
    print(separator)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()