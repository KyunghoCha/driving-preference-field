#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEMPLATE_PATH="${REPO_ROOT}/desktop/linux/driving-preference-field-parameter-lab.desktop.in"
TARGET_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
TARGET_PATH="${TARGET_DIR}/driving-preference-field-parameter-lab.desktop"
LAUNCHER_PATH="${REPO_ROOT}/desktop/linux/launch_parameter_lab.sh"
ICON_PATH="${REPO_ROOT}/assets/parameter_lab_launcher.svg"

mkdir -p "${TARGET_DIR}"

if [[ ! -f "${TEMPLATE_PATH}" ]]; then
    echo "Desktop entry template not found: ${TEMPLATE_PATH}" >&2
    exit 1
fi

if [[ ! -x "${LAUNCHER_PATH}" ]]; then
    echo "Launcher script is missing or not executable: ${LAUNCHER_PATH}" >&2
    exit 1
fi

if [[ ! -f "${ICON_PATH}" ]]; then
    echo "Icon file not found: ${ICON_PATH}" >&2
    exit 1
fi

sed \
    -e "s|@REPO_ROOT@|${REPO_ROOT}|g" \
    -e "s|@LAUNCHER_PATH@|${LAUNCHER_PATH}|g" \
    -e "s|@ICON_PATH@|${ICON_PATH}|g" \
    "${TEMPLATE_PATH}" > "${TARGET_PATH}"

chmod 0644 "${TARGET_PATH}"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${TARGET_DIR}" >/dev/null 2>&1 || true
fi

printf 'Installed desktop entry: %s\n' "${TARGET_PATH}"
