#!/usr/bin/env bash
# Pornește aplicația HelpDesk IT local.
# Utilizare:  bash scripts/run.sh [--reset] [--port 5000]
#   --reset   recreează baza de date cu datele de test (șterge tichetele existente)
#   --port    portul pe care pornește serverul (implicit 5000)
set -euo pipefail

cd "$(dirname "$0")/.."

PORT=5000
RESET=0
while [ $# -gt 0 ]; do
  case "$1" in
    --reset) RESET=1 ;;
    --port) PORT="${2:?Lipsește valoarea pentru --port}"; shift ;;
    *) echo "Opțiune necunoscută: $1" >&2; exit 1 ;;
  esac
  shift
done

PYTHON="$(command -v python3.12 || command -v python3)"

if [ ! -x .venv/bin/python ]; then
  echo "== Creez mediul virtual (.venv) cu $PYTHON"
  "$PYTHON" -m venv .venv
fi

# Reinstalează dependențele doar când requirements.txt s-a schimbat
if [ ! -f .venv/.instalat ] || [ requirements.txt -nt .venv/.instalat ]; then
  echo "== Instalez dependențele"
  .venv/bin/pip install -q --disable-pip-version-check -r requirements.txt
  touch .venv/.instalat
fi

if [ "$RESET" = 1 ] || [ ! -f instance/helpdesk.db ]; then
  echo "== Creez baza de date cu datele de test"
  .venv/bin/python seed.py
fi

echo "== HelpDesk IT pornește pe http://127.0.0.1:$PORT  (Ctrl+C pentru oprire)"
echo "   Conturi de test: angajat@technova.test, tehnician@technova.test,"
echo "   manager@technova.test – parola: parola123"
exec .venv/bin/flask --app app run --port "$PORT" --debug
