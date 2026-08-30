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
SNAPSHOT_ID="${1:-latest}"
RESTORE_TEST_PARENT="${RESTIC_RESTORE_TEST_PARENT:-/tmp}"

command -v "${RESTIC_BIN}" >/dev/null 2>&1 || fail "Restic executable not found: ${RESTIC_BIN}"
[[ -d "${JARVIS_ROOT}" ]] || fail "JARVIS_ROOT is not a directory: ${JARVIS_ROOT}"
[[ -f "${RESTIC_PASSWORD_FILE}" && -r "${RESTIC_PASSWORD_FILE}" ]] || \
    fail "RESTIC_PASSWORD_FILE is missing or unreadable: ${RESTIC_PASSWORD_FILE}"
[[ -d "${RESTORE_TEST_PARENT}" && -w "${RESTORE_TEST_PARENT}" ]] || \
    fail "Restore test parent is missing or not writable: ${RESTORE_TEST_PARENT}"

JARVIS_ROOT="$(cd "${JARVIS_ROOT}" && pwd -P)"
restore_dir="$(mktemp -d "${RESTORE_TEST_PARENT%/}/jarvis-restic-restore-test.XXXXXX")"

cleanup() {
    case "${restore_dir}" in
        "${RESTORE_TEST_PARENT%/}"/jarvis-restic-restore-test.*)
            rm -rf -- "${restore_dir}"
            ;;
        *)
            printf 'WARNING: refusing to remove unexpected restore path: %s\n' "${restore_dir}" >&2
            ;;
    esac
}
trap cleanup EXIT

printf 'Checking Restic repository integrity...\n'
"${RESTIC_BIN}" check

printf 'Restoring snapshot %s to temporary path %s...\n' "${SNAPSHOT_ID}" "${restore_dir}"
"${RESTIC_BIN}" restore "${SNAPSHOT_ID}" --target "${restore_dir}"

restored_root="${restore_dir}${JARVIS_ROOT}"
[[ -d "${restored_root}" ]] || fail "Restored JARVIS root was not found: ${restored_root}"

verified=0
compare_item() {
    local source_path="$1"
    local restored_path="${restore_dir}${source_path}"

    [[ -e "${restored_path}" ]] || fail "Restored item is missing: ${source_path}"
    if [[ -d "${source_path}" ]]; then
        diff --no-dereference --recursive --brief "${source_path}" "${restored_path}" >/dev/null || \
            fail "Restored directory differs from source: ${source_path}"
    else
        cmp --silent "${source_path}" "${restored_path}" || \
            fail "Restored file differs from source: ${source_path}"
    fi
    printf 'Verified restored item: %s\n' "${source_path}"
    verified=$((verified + 1))
}

[[ -d "${JARVIS_ROOT}/data" ]] && compare_item "${JARVIS_ROOT}/data"
[[ -f "${JARVIS_ROOT}/logs/audit.jsonl" ]] && compare_item "${JARVIS_ROOT}/logs/audit.jsonl"
[[ -f "${JARVIS_ROOT}/.env" ]] && compare_item "${JARVIS_ROOT}/.env"

if [[ -n "${JARVIS_BACKUP_PATHS_FILE:-}" ]]; then
    [[ -f "${JARVIS_BACKUP_PATHS_FILE}" && -r "${JARVIS_BACKUP_PATHS_FILE}" ]] || \
        fail "JARVIS_BACKUP_PATHS_FILE is missing or unreadable: ${JARVIS_BACKUP_PATHS_FILE}"
    while IFS= read -r extra_path || [[ -n "${extra_path}" ]]; do
        [[ -z "${extra_path}" || "${extra_path}" == \#* ]] && continue
        [[ "${extra_path}" == /* ]] || fail "Extra verification paths must be absolute: ${extra_path}"
        compare_item "${extra_path}"
    done < "${JARVIS_BACKUP_PATHS_FILE}"
fi

(( verified > 0 )) || fail "No durable source items were available for restore comparison"
printf 'Restore verification succeeded for %d durable item(s).\n' "${verified}"
