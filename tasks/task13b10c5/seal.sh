#!/usr/bin/env bash
# Seal the C5 evidence bundle. SHA256SUMS never contains itself.
set -uo pipefail
E=/home/jarvis/.hermes-poc/evidence/task13b10c5-operational-utility
cd "$E" || exit 1
find "$E" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
rm -f "$E/SHA256SUMS"
LIST=$(mktemp /tmp/c5-seal-list.XXXXXX)
OUT=$(mktemp /tmp/c5-seal-sums.XXXXXX)
find . -type f ! -name SHA256SUMS | sed 's|^\./||' | LC_ALL=C sort > "$LIST"
while IFS= read -r f; do sha256sum "$f"; done < "$LIST" > "$OUT"
mv "$OUT" "$E/SHA256SUMS"
rm -f "$LIST"
echo "files_total=$(find . -type f | wc -l)"
echo "manifest_entries=$(wc -l < SHA256SUMS)"
echo "pycache=$(find . -name '__pycache__' | wc -l)"
echo "verify_failures=$(sha256sum -c SHA256SUMS 2>/dev/null | grep -vc ': OK')"
echo "verify_ok=$(sha256sum -c SHA256SUMS 2>/dev/null | grep -c ': OK')"
echo "sha256sums_sha256=$(sha256sum SHA256SUMS | cut -d' ' -f1)"
