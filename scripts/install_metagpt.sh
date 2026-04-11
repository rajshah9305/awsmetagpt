#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo "Creating .venv with python3.11 (MetaGPT PyPI builds target CPython 3.9–3.11)..."
  python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -U pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-metagpt.txt

echo ""
echo "Verify import:"
python -c "from metagpt.software_company import generate_repo; from metagpt.team import Team; print('MetaGPT import OK')"

echo ""
echo "Optional (browser / scraping tools used by some MetaGPT features):"
echo "  playwright install"
