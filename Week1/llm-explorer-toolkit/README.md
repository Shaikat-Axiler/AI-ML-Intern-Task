# 🧪 LLM Explorer Toolkit

A beautiful, interactive toolkit for comparing outputs from different open-source LLMs using various prompting strategies — side by side.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Side-by-side comparison** | Run any two models with the same prompt simultaneously |
| **5 prompting techniques** | Zero Shot, One Shot, Few Shot, Chain of Thought, Role Play |
| **4+ models supported** | Mistral 7B, Llama 3 8B, Gemma 7B, Phi-3 Mini (cloud) + Ollama local models |
| **Response quality ratings** | 1–5 star rating per model response with optional comment |
| **Favourites & tagging** | Save, title, and tag your best comparison sessions |
| **Usage statistics** | Visual breakdown of technique & model usage, average ratings |
| **Session history** | Browse all past comparison sessions |

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/llm-explorer-toolkit.git
cd llm-explorer-toolkit
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
# Free API key from https://openrouter.ai (sign up, no credit card needed for free models)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx

# Only needed if using local Ollama models
OLLAMA_BASE_URL=http://localhost:11434
```

### 5. Run the server

```bash
uvicorn app:app --reload --port 8000
```

Open **http://localhost:8000** in your browser. 🎉

---

## 🏗️ Project Structure

```
llm-explorer-toolkit/
├── app.py                  # Entry point (uvicorn target)
├── requirements.txt
├── .env.example
│
├── backend/
│   ├── __init__.py
│   ├── main.py             # FastAPI routes
│   ├── models.py           # Model manager + prompting techniques
│   └── storage.py          # JSON file-based persistence
│
├── frontend/
│   └── index.html          # Single-page application (vanilla JS)
│
├── data/
│   └── sessions/           # Auto-created; stores session JSON files
│
└── README.md
```

---

## 🤖 Supported Models

### Cloud Models (via OpenRouter — free tier)

| Model ID | Label | Provider |
|---|---|---|
| `mistral-7b` | Mistral 7B | Mistral AI |
| `llama3-8b` | Llama 3 8B | Meta AI |
| `gemma-7b` | Gemma 7B | Google |
| `phi-3-mini` | Phi-3 Mini 128k | Microsoft |

> All cloud models are available on OpenRouter's **free tier**. Get your key at [openrouter.ai](https://openrouter.ai).

### Local Models (via Ollama)

| Model ID | Label | Pull command |
|---|---|---|
| `ollama-llama3` | Llama 3 (Local) | `ollama pull llama3` |
| `ollama-mistral` | Mistral (Local) | `ollama pull mistral` |

Install Ollama from [ollama.com](https://ollama.com), then pull a model before using it.

---

## 💡 Prompting Techniques

| Technique | Description |
|---|---|
| **Zero Shot** | Direct prompt — tests raw model capability with no guidance |
| **One Shot** | One example provided before the main prompt |
| **Few Shot** | Multiple examples guide the model's response format |
| **Chain of Thought** | Instructs the model to reason step-by-step before answering |
| **Role Play** | Assigns a world-class expert persona to the model |

---

## 📖 Usage Examples

### Compare reasoning styles

1. Select **Mistral 7B** as Model A and **Llama 3 8B** as Model B
2. Choose **Chain of Thought** technique
3. Enter: *"If I have 3 apples and give away half, then buy 5 more, how many do I have?"*
4. Click **Run Comparison**

### Benchmark instruction following

1. Select **Phi-3 Mini** vs **Gemma 7B**
2. Choose **Few Shot**
3. Enter: *"Write a Python function that reverses a linked list"*

### Test creative writing with persona

1. Select any two models
2. Choose **Role Play**
3. Enter: *"Explain quantum entanglement to a 10-year-old"*

---

## 🛠️ API Reference

The backend exposes a REST API (useful for scripting or extending):

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/models` | List available models |
| GET | `/api/techniques` | List prompting techniques |
| POST | `/api/compare` | Run a comparison session |
| POST | `/api/rate` | Submit a rating for a response |
| POST | `/api/favorites` | Save a session as favourite |
| DELETE | `/api/favorites/{id}` | Remove from favourites |
| GET | `/api/favorites` | List all favourites |
| GET | `/api/sessions` | List recent sessions |
| GET | `/api/sessions/{id}` | Get a session by ID |
| GET | `/api/stats` | Usage statistics |

Interactive docs available at **http://localhost:8000/docs**

---

## ➕ Adding New Models

Edit `backend/models.py` and add an entry to the `MODELS` dict:

```python
"my-model": {
    "label": "My Custom Model",
    "provider": "openrouter",            # or "ollama"
    "model_id": "org/model-name:free",   # OpenRouter model string
    "description": "A brief description.",
    "color": "#FF6B6B",
    "badge": "Custom",
},
```

---

## 🗄️ Data Storage

Sessions are stored as JSON files in `data/sessions/`. Each file contains:
- Full prompt and responses from both models
- Latency and token counts
- Applied prompting technique + effective prompts sent to the API
- Ratings and comments
- Favourite status, title, and tags

To reset all data: `rm -rf data/sessions/`

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push and open a PR

---

## 📄 License

MIT © 2024
