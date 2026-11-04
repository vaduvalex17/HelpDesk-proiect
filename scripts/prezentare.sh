#!/usr/bin/env bash
# Pornește HelpDesk IT pentru prezentare și deschide browserul (Linux / macOS).
# Utilizare:  bash scripts/prezentare.sh [--pastreaza]
# Toată logica e în prezentare.py; aici doar găsim un Python 3 și îl rulăm.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="$(command -v python3.12 || command -v python3 || command -v python)"
exec "$PYTHON" scripts/prezentare.py "$@"
