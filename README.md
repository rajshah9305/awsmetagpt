# MetaGPT + AWS Bedrock + E2B

Full-stack app: **FastAPI** backend (generation, Bedrock, E2B sandboxes) and **Vite + React** frontend. Real-time progress uses **Server-Sent Events** (SSE), compatible with serverless hosts such as Vercel.

## Requirements

- Python **3.11+**
- Node.js **18+** (for the frontend)
- Optional: AWS credentials (Bedrock), `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (MetaGPT), E2B API key, and `pip install` extras as below

## Quick start (local)

```bash
cp .env.example .env
# Edit .env with your keys

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"     # optional: pytest

# Terminal 1 — API (default http://127.0.0.1:8000)
python main.py

# Terminal 2 — UI (proxies /api to :8000)
npm install
npm run dev
```

**MetaGPT** (multi-agent generation) is not in the base `requirements.txt`. Install when you need real generation runs, e.g. per [MetaGPT install notes](https://github.com/FoundationAgents/MetaGPT) and your chosen version. **E2B** SDK: `pip install e2b` when using sandboxes (`ENABLE_E2B=true`).

## Deploy (Vercel)

- `vercel.json` builds the frontend to `dist` and routes `/api/v1/*` and `/health` to the Python serverless entry `api/index.py`.
- Set Python dependencies for that function via `api/requirements.txt` (kept in sync with the project’s core backend deps).

## Environment

See `.env.example` for variables: `AWS_*`, `BEDROCK_*`, `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`, `E2B_*`, `METAGPT_WORKSPACE`, feature flags, and rate limits.

## Tests

```bash
pytest tests/ -q
```
