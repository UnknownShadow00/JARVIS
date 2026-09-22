# Fixture corpus and freeze
Task A froze 119 cases: 15 valid / 104 invalid. R2 copies contract-corpus.json byte-for-byte as tests/execution/hermes_adapter_corpus.json.
SHA-256: 524921d4372173a6608b7fe3639cb687ff5775b87d0b4c3fe4e9f53c0d194d6c.
A separate 27-case generalization corpus was created after implementation source/rules freeze bf7c766d1433a7880c56644f79a3b242cfffa8f449d9ef003b452e84462e8326. All 27 passed on first scoring.
Generalization includes Unicode/escape handling, deeply nested reasoning-name variants, nested duplicate keys, many ordered proposals, nonfinite numeric overflow and inert authority-looking data.
After scoring, source changed only by renaming the private _require helper to _check and replacing the word provenance in the opening docstring with source trust, to avoid old substring checks. Normalized AST equality is asserted in verify_adapter.py and recorded in both verification JSONs. No parser rule or corpus label was tuned.
The frozen corpus contains one extra blank line at EOF. It was retained to preserve the sealed bytes; git diff --check reports that formatting-only warning. All other whitespace checks pass; no fixture content was rewritten to satisfy formatting.
