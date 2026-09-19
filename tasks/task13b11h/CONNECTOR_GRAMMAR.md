# Task 13B11H — Frozen Connector Grammar

Taken verbatim from `tasks/task13b10c4/connector-grammar.json`, status
**"FROZEN BEFORE SCORING"**. Contract §5.3 requires a compound request to be segmented
deterministically **before** the primary action is chosen, so that a reporting or conditional
clause cannot displace the action clause.

## 1. Segmentation

Connector words: `and then`, `after that`, `and`, `then`, `once`, `when`, `if`, `but`, `so`.
Punctuation separators: `;`, `,`, newline.

```
split:  (?:\s*[;,\n]+\s*|\s+(?:and\s+then|after\s+that|and|then|once|when|if|but|so)\s+)
```

Case-insensitive, applied once to the whole request. Empty fragments are discarded. The longer
alternatives precede the shorter ones so `and then` is consumed as one connector rather than as
`and` followed by a stray `then`.

## 2. Per-clause prefixes and guards

```
polite/temporal:  ^(?:(?:please|kindly|now|also|just|first|next|go\s+ahead\s+and|could\s+you
                   |can\s+you|would\s+you|will\s+you|i\s+need\s+you\s+to|i\s+want\s+you\s+to
                   |you\s+should)\s+)+
negation:         ^(?:do\s+not|don't|dont|never|no\s+need\s+to|without|avoid)\b
reporting start:  ^(?:tell\s+me|let\s+me\s+know|keep\s+me\s+posted|report(?:\s+back)?|confirm
                   |notify\s+me|inform\s+me|show\s+me|update\s+me|say)\b
```

A clause is classified into exactly one `ClauseKind`, in this frozen order:

| Order | Kind | Condition |
|---|---|---|
| 1 | `REPORTING` | the core matches the reporting-start pattern |
| 2 | `NEGATED` | the core matches the negation pattern |
| 3 | `ACTION` | the clause-initial token is in the action lexicon |
| 4 | `NONE` | anything else |

Reporting is tested before negation and both before the verb, so "don't deploy" and "tell me when
the deploy finishes" can never be read as a deploy instruction. This ordering is the rule, not an
artefact of which `if` came first: it is asserted by test.

## 3. The connector never implies a second action

Verbatim from the frozen grammar: *"A connector never implies a second tool call. One supported
primary action is preserved unless a second explicit supported action is actually present, in which
case the request is refused as MULTI_ACTION_UNSUPPORTED."*

This is the C3 → C4 fix. Before segmentation, a whole-string classifier lost the primary action
whenever a reporting clause was present — contract §7.3 records J04, J05 and J06 each scoring 0/5
in 13B10C3 and 5/5 after segmentation in 13B10C4, holding at 5/5 in 13B10C5. All three are in the
frozen regression corpus.

## 4. Regex safety

Five module-level patterns for the grammar plus the reporting and target patterns, all compiled
once from string literals. No pattern is built from user text. No nested quantifier: the only
repetition over a group is the polite-prefix `(?:…\s+)+`, whose alternatives are fixed literals
that each consume at least one non-space token followed by mandatory whitespace, so it cannot
backtrack quadratically on an unmatched suffix. Asserted by a static test and re-checked in the
security review.

## 5. What this is not

Not a natural-language parser. There is no grammar induction, no part-of-speech tagging, no
dependency parse, no NLP dependency. A request whose structure the frozen grammar cannot resolve
falls through to `PrimaryAction.NONE` or to an unresolved target — never to a guess.
