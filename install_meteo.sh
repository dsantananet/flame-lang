#!/usr/bin/env bash
set -euo pipefail
meteo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd "$meteo_root"
python3 -c 'import sys; assert sys.version_info >= (3,10), "Requer Python 3.10+"'
if [ "${1:-}" = '--with-encryption' ]; then
  python3 -m venv .venv-meteo
  .venv-meteo/bin/python -m pip install -r requirements-meteo-crypto.txt
fi
python3 -B tools/export_ipma.py --output "${METEO_OUTPUT_DIR:-$meteo_root/meteo-data}"
printf '%s\n' 'Dados preparados. Arranque: python3 -B meteo_server.py; aplicação no caminho /web/meteo/.'
