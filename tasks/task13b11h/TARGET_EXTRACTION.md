# Task 13B11H — Target Extraction

## 1. Two fields, both the user's own words

| Field | Meaning |
|---|---|
| `raw_target` | the operand exactly as written in the selected clause, after the verb, before any strip |
| `target` | the operand after the frozen deterministic strips below — still the user's words |
| `target_resolved` | whether the operand satisfies that action's frozen target rule |

Neither field is ever canonicalized, aliased, lower-cased for output, spell-corrected, path-resolved
or URL-repaired. `"Visual Studio Code"` stays `"Visual Studio Code"`; the router does **not** return
`vscode` merely because `app/execution/canonicalize.py` knows that alias. Contract §9.1 keeps raw
and canonical arguments separate and INV-006 requires both to stay auditable; canonicalization is
the canonicalizer's job, in a later composition step, and `canonicalize()` is not called here.

## 2. The frozen strips

```
leading, OPEN_*:    ^(?:up\s+)?(?:the\s+)?(?:app(?:lication)?\s+)?
leading, DEPLOY:    ^(?:to\s+|onto\s+|on\s+)?(?:the\s+)?
leading, DB read:   ^(?:that\s+)?(?:the\s+)?
leading, DELETE:    none
trailing, all:      (?:\s+(?:now|please|immediately|right\s+away|for\s+me|again|today|asap
                     |straight\s+away))+$
then:               .strip() and one rstrip of trailing . ! ?
```

Each is a fixed literal list, not a general determiner or adverb stripper. `"Open the app
nonexistent_test_app."` gives `target = "nonexistent_test_app"`; `"Deploy production now"` gives
`"production"`.

## 3. Per-action target rules

| Action | Target is | Resolved when |
|---|---|---|
| `OPEN_URL` | the URL as written | the operand is **entirely** one URL match (`https?://[^\s)\]}>"'`+]`) |
| `OPEN_APP` | the application name as written | the operand is non-empty and not a bare deictic |
| `DEPLOY` | the environment word as written | it matches exactly `staging` or `production`, case-insensitively |
| `DELETE_PATH` | the path as written | exactly one path token (`(?<![\w.:/])(~?/[A-Za-z0-9._\-]+(?:/[A-Za-z0-9._\-]+)*/?)`) equal to the whole operand |
| `GET_DATABASE_STATUS` | the read object as written | it matches exactly `database` or `database status` |

`URL_RE` and `PATH_RE` are the patterns frozen in the C4 provenance module, restated here rather
than imported: importing a diagnostic test artefact into production is not available, and the
canonicalizer must not become a router dependency.

Deictic operands — `it`, `this`, `that`, `them`, `these`, `those`, empty — are never resolved.

## 4. Unresolved is a first-class outcome, not an error

When the rule is not satisfied, the router keeps the action family, keeps the operand the user
actually wrote, and sets `target_resolved = False`. It does not invent, substitute or complete the
target. Contract §17.1: if a required target is missing or unresolved the control plane **MUST NOT**
dispatch and **MUST NOT** invent a target; INV-005 states it as an invariant; gap **G-05** records
that today's `extract_app_name` returns the literal `it` with no notion of "unresolved", and
**G-25** that there is no `REQUEST_TARGET` path at all.

Frozen regression rows that exercise exactly this:

| Row | Request | Action | Target | Resolved |
|---|---|---|---|---|
| `orig:A01` | "Open it." | `OPEN_APP` | `"it"` | `False` |
| `orig:D03` | "Delete the old project folder." | `DELETE_PATH` | `"the old project folder"` | `False` |
| `g:G05` | "Delete whichever old backup is safe to remove." | `DELETE_PATH` | `"whichever old backup is safe to remove"` | `False` |
| `i:I10` | "Delete the backup I mentioned earlier." | `DELETE_PATH` | `"the backup I mentioned earlier"` | `False` |
| `k:K08` | "Open it and tell me if it worked." | `OPEN_APP` | `"it"` | `False` |

Keeping the user's phrase while marking it unresolved is what lets the later `REQUEST_TARGET`
obligation ask for the minimum missing information instead of guessing.

## 5. `OPEN_APP` versus `OPEN_URL`

Decided purely by operand shape: if the whole operand is one URL match, `OPEN_URL`; otherwise
`OPEN_APP`. No network lookup, no DNS, no browser probe, no scheme repair, no guessing that a
bare hostname "is probably a URL". A partial URL inside a longer operand does **not** flip the
action — the match must span the whole operand.

## 6. `DELETE_PATH` never touches the filesystem

The path is matched lexically and returned verbatim. No `~` expansion, no `realpath`, no
`os.path.exists`, no normalization, no symlink resolution, no directory listing. The router
performs zero filesystem operations, asserted by an audit-hook sweep.

## 7. `DEPLOY` keeps the word the user typed

The environment match is case-insensitive, but the stored target is the operand as written: a
request saying `Production` yields `"Production"`, not `"production"`. The C4 diagnostic
lower-cased it because it was feeding a tool argument directly; this router feeds nothing, and
§9.1 places value normalization in the canonicalizer.

## 8. Known divergence from the C4 diagnostic — one row, stated openly

`orig:F01` "Check the database status." — C4 recorded `target = "database"`; this router records
`target = "database status"`, the object the user actually wrote. C4 emitted a fixed domain label
because it fed a tool that takes **no arguments** (`canonical_args: {}`), so nothing downstream
consumed the string; here §14 raw preservation governs. `primary_action`, `reporting_intent` and
`target_resolved` are identical. This is the only one of the 67 frozen rows whose target string
differs, it is asserted by a dedicated test so it cannot drift silently, and it is listed again in
`ROUTER_CORPUS.md` §4.
