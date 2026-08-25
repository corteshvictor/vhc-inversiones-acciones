#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${VHC_TEST_VENV:-${PROJECT_ROOT}/.venv}"
STAMP="${VENV_DIR}/.vhc-test-requirements"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    python3 -m venv "${VENV_DIR}"
fi

if [[ ! -f "${STAMP}" || "${PROJECT_ROOT}/requirements.txt" -nt "${STAMP}" || "${PROJECT_ROOT}/requirements-dev.txt" -nt "${STAMP}" ]]; then
    "${VENV_DIR}/bin/python" -m pip install --requirement "${PROJECT_ROOT}/requirements-dev.txt"
    touch "${STAMP}"
fi

cd "${PROJECT_ROOT}"
"${VENV_DIR}/bin/python" -m ruff check .
"${VENV_DIR}/bin/python" -m ruff format --check .
"${VENV_DIR}/bin/pyright" --pythonpath "${VENV_DIR}/bin/python"
exec "${VENV_DIR}/bin/python" -m pytest "$@"
