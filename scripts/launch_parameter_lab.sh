#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_BASE="${HOME}/anaconda3"
ENV_NAME="${LRPC_CONDA_ENV:-local-reference-path-cost}"
LEGACY_ENV_NAME="driving-preference-field"

if [[ -f "${CONDA_BASE}/etc/profile.d/conda.sh" ]]; then
    # shellcheck disable=SC1091
    source "${CONDA_BASE}/etc/profile.d/conda.sh"
elif command -v conda >/dev/null 2>&1; then
    eval "$(conda shell.bash hook)"
else
    echo "conda command was not found. Install conda or update scripts/launch_parameter_lab.sh." >&2
    exit 1
fi

if ! conda env list | awk '{print $1}' | grep -Fxq "${ENV_NAME}"; then
    if [[ -z "${LRPC_CONDA_ENV:-}" ]] && conda env list | awk '{print $1}' | grep -Fxq "${LEGACY_ENV_NAME}"; then
        echo "Using legacy conda env ${LEGACY_ENV_NAME}; set LRPC_CONDA_ENV or create local-reference-path-cost to silence this." >&2
        ENV_NAME="${LEGACY_ENV_NAME}"
    fi
fi

conda activate "${ENV_NAME}"

cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}/src"

if [[ "$#" -eq 0 ]]; then
    exec python -m local_reference_path_cost parameter-lab --case "${REPO_ROOT}/cases/toy/straight_corridor.yaml"
fi

exec python -m local_reference_path_cost parameter-lab "$@"
