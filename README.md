# 🔍 CodeReview — AI Code Review Environment

An **OpenEnv RL environment** where an AI agent reviews Python code snippets for bugs, style issues, and security vulnerabilities.

Built for the **Meta × PyTorch OpenEnv Hackathon 2026**. This environment addresses the hackathon mandate to "simulate a real-world task (NOT games or toys)" by framing the interaction as an automated pull-request review task, which AI agents are actively used for today.

## 🏆 Results

| Task | Difficulty | Reward |
|------|-----------|--------|
| easy_001 | Easy | 0.50 – 1.00 |
| easy_002 | Easy | **1.00** ✅ |
| medium_001 | Medium | **1.00** ✅ |
| medium_002 | Medium | 0.33 – 0.67 |
| hard_001 | Hard | 0.60 – 0.80 |
| hard_002 | Hard | 0.25 – 0.50 |
| **Average** | | **0.65 – 0.74** |

## 📋 Environment Overview

| Property | Value |
|----------|-------|
| Action | List of identified issues + summary |
| Observation | Code snippet, description, difficulty, feedback |
| Reward | 0.0 - 1.0 (precision/recall of found issues) |
| Tasks | 6 tasks across 3 difficulty levels |
| Steps per episode | 1 (single review submission) |

## 🎯 Action Space
- `issues`: List of dicts with `line`, `severity`, `category`, `description`
- `summary`: Overall code quality summary

## 👁️ Observation Space
- `code_snippet`: Python code to review
- `task_description`: What the code is supposed to do
- `difficulty`: "easy" | "medium" | "hard"
- `num_hidden_issues`: Number of issues to find
- `feedback`: Grader feedback after submission

## 📊 Difficulty Tiers
- **Easy**: Division by zero, missing error handling, resource management (2 issues each)
- **Medium**: Off-by-one errors, integer overflow, missing kwargs, unbounded caches (3 issues each)
- **Hard**: Weak cryptography (MD5), timing attacks, authorization gaps, thread safety, memory leaks (4-5 issues each)

## ⚙️ Grader Configuration
The environment uses a **fuzzy matching** technique on the `category` (exact match) and significant `description` terms (30% keyword overlap) to compare the AI's predictions with ground-truth data.

Partial rewards are calculated based on **Precision and Recall**. Weights are adapted based on task difficulty:
- **Easy**: precision: 0.3, recall: 0.7
- **Medium**: precision: 0.4, recall: 0.6
- **Hard**: precision: 0.5, recall: 0.5

## 🔧 Key Technical Features
- **17-Point Security Review Checklist** — ensures the LLM systematically checks for concurrency, memory leaks, crypto flaws, authorization gaps, and more
- **Structured JSON Output** — uses `response_format={"type": "json_object"}` for reliable parsing
- **Robust Fallback Parsing** — regex extraction + YAML fallback for malformed LLM outputs
- **Rate Limit Retry** — automatic 60-second backoff with 5 retries for API quota errors
- **Category Alignment** — precise mapping of bug types to grader-expected categories

## 🚀 Setup

```bash
pip install -e ".[inference]"
pip install openenv-core pyyaml
```

### Start the Server
```bash
uvicorn code_review_env.server.app:app --host 0.0.0.0 --port 8000
```

### Run Inference
```bash
export OPENAI_API_KEY="your_api_key_here"
export API_BASE_URL="https://api.groq.com/openai/v1"
export MODEL_NAME="llama-3.3-70b-versatile"

python inference.py
```

**PowerShell (Windows):**
```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
$env:API_BASE_URL = "https://api.groq.com/openai/v1"
$env:MODEL_NAME = "llama-3.3-70b-versatile"

python inference.py
```

> **Note:** The inference script supports any OpenAI-compatible API (Groq, Google Gemini, OpenAI, etc.)

## 🐳 Docker Deployment

```bash
docker build -f server/Dockerfile -t code-review-env .
docker run -p 8000:8000 code-review-env
```

## 🛠️ Tech Stack
- **Framework**: FastAPI + WebSockets (via `openenv-core`)
- **Models**: Pydantic v2 for Action, Observation, State schemas
- **LLM**: Groq (LLaMA 3.3 70B) via OpenAI-compatible API
- **Containerization**: Docker
- **Deployment**: Hugging Face Spaces

## 📁 Project Structure
```
code_review_env/
├── __init__.py              # Package exports
├── models.py                # Pydantic schemas (Action, Observation, State)
├── client.py                # WebSocket client for the environment
├── inference.py             # Baseline AI agent with 17-point review checklist
├── openenv.yaml             # OpenEnv environment registration
├── pyproject.toml           # Python project config
├── README.md                # This file
├── server/
│   ├── app.py               # FastAPI application
│   ├── environment.py       # RL environment logic (reset/step)
│   ├── grader.py            # Precision/Recall fuzzy grader
│   ├── Dockerfile           # Container deployment
│   └── requirements.txt     # Server dependencies
└── tasks/
    ├── __init__.py
    └── task_bank.py          # 6 tasks across 3 difficulty tiers
```

## 📄 License
MIT
