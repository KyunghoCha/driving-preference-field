#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_BASE="${HOME}/anaconda3"
ENV_NAME="driving-preference-field"

if [[ -f "${CONDA_BASE}/etc/profile.d/conda.sh" ]]; then
    # shellcheck disable=SC1091
    source "${CONDA_BASE}/etc/profile.d/conda.sh"
elif command -v conda >/dev/null 2>&1; then
    eval "$(conda shell.bash hook)"
else
    echo "conda command was not found. Install conda or update scripts/launch_parameter_lab.sh." >&2
    exit 1
fi

conda activate "${ENV_NAME}"

cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}/src"

if [[ "$#" -eq 0 ]]; then
    exec python -m driving_preference_field parameter-lab --case "${REPO_ROOT}/cases/toy/straight_corridor.yaml"
fi

exec python -m driving_preference_field parameter-lab "$@"
