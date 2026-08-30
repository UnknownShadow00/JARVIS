#!/usr/bin/env bash
set -euo pipefail

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 2
}

: "${RESTIC_REPOSITORY:?ERROR: RESTIC_REPOSITORY is required}"
: "${RESTIC_PASSWORD_FILE:?ERROR: RESTIC_PASSWORD_FILE is required}"

RESTIC_BIN="${RESTIC_BIN:-restic}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
DEFAULT_JARVIS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd -P)"
JARVIS_ROOT="${JARVIS_ROOT:-${DEFAULT_JARVIS_ROOT}}"
EXCLUDE_FILE="${JARVIS_RESTIC_EXCLUDE_FILE:-${JARVIS_ROOT}/config/restic-excludes.txt}"

command -v "${RESTIC_BIN}" >/dev/null 2>&1 || fail "Restic executable not found: ${RESTIC_BIN}"
[[ -d "${JARVIS_ROOT}" ]] || fail "JARVIS_ROOT is not a directory: ${JARVIS_ROOT}"
[[ -f "${RESTIC_PASSWORD_FILE}" && -r "${RESTIC_PASSWORD_FILE}" ]] || \
    fail "RESTIC_PASSWORD_FILE is missing or unreadable: ${RESTIC_PASSWORD_FILE}"
[[ -f "${EXCLUDE_FILE}" && -r "${EXCLUDE_FILE}" ]] || \
    fail "Restic exclude file is missing or unreadable: ${EXCLUDE_FILE}"

JARVIS_ROOT="$(cd "${JARVIS_ROOT}" && pwd -P)"
sources=("${JARVIS_ROOT}")

if [[ -n "${JARVIS_BACKUP_PATHS_FILE:-}" ]]; then
    [[ -f "${JARVIS_BACKUP_PATHS_FILE}" && -r "${JARVIS_BACKUP_PATHS_FILE}" ]] || \
        fail "JARVIS_BACKUP_PATHS_FILE is missing or unreadable: ${JARVIS_BACKUP_PATHS_FILE}"

    while IFS= read -r extra_path || [[ -n "${extra_path}" ]]; do
        [[ -z "${extra_path}" || "${extra_path}" == \#* ]] && continue
        [[ "${extra_path}" == /* ]] || fail "Extra backup paths must be absolute: ${extra_path}"
        [[ -e "${extra_path}" ]] || fail "Extra backup path does not exist: ${extra_path}"
        sources+=("${extra_path}")
    done < "${JARVIS_BACKUP_PATHS_FILE}"
fi

tag_args=(--tag jarvis)
if [[ -n "${JARVIS_BACKUP_TAG:-}" ]]; then
    tag_args+=(--tag "${JARVIS_BACKUP_TAG}")
fi

printf 'Backing up JARVIS from %s\n' "${JARVIS_ROOT}"
printf 'Repository: %s\n' "${RESTIC_REPOSITORY}"
printf 'Host: %s\n' "$(hostname)"

"${RESTIC_BIN}" backup \
    --one-file-system \
    --exclude-file "${EXCLUDE_FILE}" \
    "${tag_args[@]}" \
    "${sources[@]}"

printf '\nLatest JARVIS snapshot:\n'
"${RESTIC_BIN}" snapshots --latest 1 --tag jarvis
printf 'Backup completed successfully.\n'
