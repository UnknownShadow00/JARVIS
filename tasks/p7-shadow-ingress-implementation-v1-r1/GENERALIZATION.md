# Separately frozen unseen corpus

20 cases frozen before the first scored focused run. SHA256: `262c5b628c0e0c300a6558d06a017e3e8f0592cf7366b692e4cc01f660cf8b2e`. Expected outcomes are stored separately under `generalization-corpus/expectations.json`; source and outcomes are covered by the pre-code freeze.

Coverage: Unicode/combining forms, whitespace/empty text, embedded NUL, long valid text, unsupported action wording, URL-like text, fake authority-like text/metadata and alternate REST/WS fixture labels. All text is preserved without semantic classification. Labels are not production schema fields.

First unseen execution: 20 passed, zero forbidden events and no authority promotion. No unseen expectation/source was changed. The corpus is external evidence rather than additional production-routing tests. It does not claim live transport or model coverage.
