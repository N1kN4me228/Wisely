#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --clean Wisely.spec

# Ship the AI key with the build so the binary works out of the box.
# This does NOT bake the key into the compiled program: it copies your
# local .env (never committed — see .gitignore) next to the frozen
# binary, which is exactly what ai_engine.py already looks for at
# startup. Anyone with the binary can also read this .env in plain
# text, so only do this for builds you control the distribution of.
if [ -f ".env" ]; then
    cp .env "dist/.env"
    echo "Copied .env next to the built binary - AI works immediately."
else
    echo "No .env in project root - the build will show \"AI unavailable\" until"
    echo "a .env with GEMINI_API_KEY is placed next to the binary."
fi

printf '\nBuild complete: %s\n' "$(pwd)/dist/Wisely"
