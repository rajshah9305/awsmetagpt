# MetaGPT + AWS Bedrock + E2B

Full-stack app: **FastAPI** backend (generation, Bedrock, E2B sandboxes) and **Vite + React** frontend. Real-time progress uses **Server-Sent Events** (SSE), compatible with serverless hosts such as Vercel. Generation uses **[MetaGPT](https://github.com/FoundationAgents/MetaGPT)** (`Team` / `generate_repo` flow from upstream).

## Requirements

- Python **3.11.x** for local generation (PyPI `metagpt` targets below 3.12; the API alone can run on newer Python if you skip MetaGPT)
- Node.js **18+** (for the frontend)
- Optional: AWS credentials (Bedrock), `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (for MetaGPT’s LLM calls), E2B API key, and extras below

## Quick start (local)

```bash
cp .env.example .env
# Edit .env with your keys

python3.11 -m venv .venv   # recommended for MetaGPT
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"     # optional: pytest

# Terminal 1 — API (default http://127.0.0.1:8000)
python main.py

# Terminal 2 — UI (proxies /api to :8000)
npm install
npm run dev
```

### Install MetaGPT (multi-agent generation)

The base `requirements.txt` does not include MetaGPT so the API and Vercel bundle stay lean. For **`POST /api/v1/generate`** to run [MetaGPT](https://github.com/FoundationAgents/MetaGPT) agents locally:

```bash
source .venv/bin/activate
pip install -r requirements-metagpt.txt
# same effect:
# pip install -e ".[metagpt]"
```

Install **after** `pip install -r requirements.txt` so MetaGPT’s pins stay compatible with the API stack. If you use `pip install -e .` later and imports fail, reinstall MetaGPT: `pip install -r requirements-metagpt.txt`.

Or use the helper (creates/uses `.venv`, installs base + MetaGPT):

```bash
./scripts/install_metagpt.sh
```

Installation can take several minutes while pip resolves MetaGPT’s pinned tree (`faiss-cpu`, `semantic-kernel`, etc.). If something fails on your platform, see the [MetaGPT repository](https://github.com/FoundationAgents/MetaGPT) (issues, Docker, or `conda`).

Optional browser tooling used by some MetaGPT features: `playwright install` inside the same environment.

**E2B** sandboxes: `pip install e2b` when `ENABLE_E2B=true` (also included in `pip install -e ".[full]"`).

## Deploy (Vercel)

- `vercel.json` builds the frontend to `dist` and routes `/api/v1/*` and `/health` to the Python serverless entry `api/index.py`.
- Set Python dependencies for that function via `api/requirements.txt` (kept in sync with the project’s core backend deps).

## Environment

See `.env.example` for variables: `AWS_*`, `BEDROCK_*`, `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`, `E2B_*`, `METAGPT_WORKSPACE`, feature flags, and rate limits.

## Tests

```bash
pytest tests/ -q
```
