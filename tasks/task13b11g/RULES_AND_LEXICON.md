# Task 13B11G — Rules and Lexicon

Frozen before implementation. The lexicon is **data**: module-level immutable sets and a small
number of bounded, literal regexes. There is no runtime learning, no alias added from a test
failure, and no pattern built from user text.

## 1. Normalization used for matching only

| Step | What |
|---|---|
| `strip()` | leading/trailing whitespace |
| whitespace collapse | runs of whitespace → one space |
| `casefold()` | case-insensitive matching |
| polite/temporal prefix removal | an optional leading `please`, `could you`, `can you`, `would you`, `now`, `then`, `next`, `also`, `and` |
| leading-clause cut | the text up to the first frozen connector or clause terminator |

Prefix removal runs **before** the clause cut, because a request may legitimately open with
`then`, which is both a sequencing prefix and a clause connector; cutting first would leave an
empty clause.

The **raw request is preserved verbatim** on the result and is never rewritten. Normalization
produces a matching key only.

**Leading-clause cut.** Contract §5.3 requires a compound request to be segmented deterministically
before the *primary action* is chosen, and §5.4 records that the validated implementation
recognises an action verb only in clause-initial position. Full segmentation and `MULTI_ACTION` are
router work (§5.2, §8) and are **not** done here. The classifier looks only at the leading clause —
the text before the first connector — which is what "clause-initial" needs and no more. Connector
set, frozen: `and then`, `after that`, `then`, `once`, `when`, `if`, `but`, `so`, `and`, plus `;`,
`,` and newline.

## 2. Lexicon categories

| Category | Members (frozen) |
|---|---|
| `ACTION_VERBS` | open, launch, start, run, execute, install, create, make, write, add, move, copy, rename, set, update, change, enable, disable, restart, reboot, shutdown, stop, kill, delete, remove, drop, purge, wipe, erase, destroy, uninstall, revoke, deploy, release, publish, push, send, email, message, post, pay, purchase, buy, transfer |
| `SENSITIVE_ACTION_VERBS` (a subset) | delete, remove, drop, purge, wipe, erase, destroy, uninstall, revoke, deploy, release, publish, push, send, email, message, post, pay, purchase, buy, transfer, restart, reboot, shutdown, stop, kill |
| `STATUS_VERBS` | check, verify, confirm, get, show, list, look, ping, test, inspect, read, fetch, query |
| `AMBIGUOUS_REFERENTS` | it, this, that, these, those, them, they, there, here, one, the app, the application, the file, the folder, the directory, the service, the server, the thing |
| `YES_NO_OPENERS` | is, are, was, were, do, does, did, has, have, had, can, could, will, would, should, am |
| `DECLARATIVE_MARKERS` | is, are, was, were, uses, using, runs, running, set, listens, points, lives, succeeded, failed, completed, passed, broke, correction, actually, sorry |
| `QUESTION_OPENERS` | what, which, who, whom, whose, where, when, why, how |

`SENSITIVE_ACTION_VERBS ⊂ ACTION_VERBS` is asserted by test.

Membership is exact set membership on a whole token after normalization. There is no prefix,
suffix, substring, stem or similarity test anywhere.

## 3. Frozen regexes

Five, all literal, all anchored or bounded, none built from user input, none with nested
quantifiers:

| Name | Pattern (verbatim) | Used for |
|---|---|---|
| `_WHITESPACE` | `\s+` | whitespace collapse |
| `_CLAUSE_SPLIT` | `[;,\n]\|\b(?:and then\|after that\|then\|once\|when\|if\|but\|so\|and)\b` | leading-clause cut |
| `_EXPLANATION` | `^(?:what (?:is\|are\|does\|do\|did)\b\|why\b\|how\b\|explain\b\|define\b\|describe\b\|tell me (?:about\|what)\b)` | definitional/explanatory form |
| `_SELF_REFERENCE` | `\b(?:i (?:said\|told\|set\|chose\|specified\|gave\|mentioned)\|did i (?:say\|tell\|set\|choose\|specify\|mention)\|you (?:were told\|have))\b` | a question about a value the user supplied earlier |
| `_FACT_KEY` | `^[a-z][a-z0-9_]*$` | validating caller-supplied context keys |

`_FACT_KEY` mirrors the shape `app/execution/provenance.py` already enforces. It is restated here
rather than imported, because importing P2 into the classifier would create exactly the dependency
this phase must not have.

## 4. Candidate fact keys

A question may be asking for the current value of a fact the control plane already holds. Deciding
that needs no parsing and no ontology — only a lookup against the caller's own key set.

Candidates are formed deterministically: the normalized leading clause is split on spaces, each
token is stripped of surrounding punctuation, tokens in the frozen `STOPWORDS` set are treated as
breaks, and every contiguous run of one, two or three remaining tokens is joined with `_`. Each
candidate is then tested for **exact** membership in `ClassifierContext.known_fact_keys`.

`STOPWORDS`, frozen: the articles and determiners (`a`, `an`, `the`, `my`, `our`, `your`, `their`,
`this`, `that`, `these`, `those`), the interrogatives (`what`, `which`, `who`, `whom`, `whose`,
`where`, `when`, `why`, `how`), the pronouns (`i`, `you`, `we`, `they`, `it`, `me`, `us`, `them`),
the auxiliaries and copulas (`is`, `are`, `was`, `were`, `be`, `been`, `am`, `do`, `does`, `did`,
`has`, `have`, `had`, `can`, `could`, `will`, `would`, `should`, `may`, `might`, `must`), the
common prepositions and conjunctions (`to`, `of`, `for`, `in`, `on`, `at`, `by`, `with`, `from`,
`about`, `into`, `over`, `and`, `or`, `but`, `as`, `than`, `then`), and the reporting verbs the
self-reference form uses (`say`, `said`, `tell`, `told`, `set`, `choose`, `chose`, `specify`,
`specified`, `give`, `gave`, `mention`, `mentioned`, `use`, `uses`, `used`).

`"what is the deployment target?"` → candidates `deployment`, `target`, `deployment_target`.
`"what did I say the port was?"` → candidate `port`.
`"what is blue-green deployment?"` → candidates `blue-green`, `deployment`, `blue-green_deployment`.

A candidate is only ever *looked up*. No key is invented, no value is read, no fuzzy match is
attempted, and a candidate that is not a legal fact key simply cannot match anything in the set.

**Documented limitation.** Matching is exact and context-driven, so a definitional question whose
nouns happen to equal a fact key the control plane holds — `"what is deployment?"` while a fact key
`deployment` is current — classifies as `VALUE_QUERY` rather than `GENERAL_EXPLANATION`. This is a
deliberate trade: the alternative is a noun ontology, which would be model inference or
benchmark-specific string matching, both forbidden by §5.3. Both readings are safe, because
`VALUE_QUERY` is the more conservative of the two — it is an always-operational lane class, so the
turn cannot expose raw model prose.

## 5. Rule table

Each rule carries a stable id, the class it produces, its reason, and its precedence rank. The
table is a tuple in precedence order; evaluation is first match wins and the order is the data, not
the order of `if` statements.

| Rank | Rule id | Condition (on the normalized leading clause) | Class | Reason |
|---|---|---|---|---|
| 1 | `R-01-action-ambiguous` | opens with an `ACTION_VERBS` token **and** the remainder is empty or is exactly an `AMBIGUOUS_REFERENTS` phrase | `AMBIGUOUS_ACTION` | `action_target_ambiguous` |
| 2 | `R-02-action-sensitive` | opens with a `SENSITIVE_ACTION_VERBS` token and has a concrete remainder | `CONFIRMATION_SENSITIVE_ACTION` | `sensitive_action_request` |
| 3 | `R-03-action-explicit` | opens with any other `ACTION_VERBS` token and has a concrete remainder | `ACTION_REQUEST` | `explicit_action_request` |
| 4 | `R-04-status-explicit` | opens with a `STATUS_VERBS` token and has a remainder | `STATUS_CHECK_REQUEST` | `explicit_status_check` |
| 5 | `R-05-value-supplied` | is a question, matches `_SELF_REFERENCE`, and a candidate key is in `known_fact_keys` | `VALUE_QUERY` | `asks_for_supplied_or_current_value` |
| 6 | `R-06-context-missing` | is a question, matches `_SELF_REFERENCE`, and no candidate key is known | `MISSING_CONTEXT_QUERY` | `referenced_value_not_in_context` |
| 7 | `R-07-value-current` | is a question opening with `what`/`which` and a candidate key is in `known_fact_keys` | `VALUE_QUERY` | `asks_for_current_known_value` |
| 8 | `R-08-explanation` | matches `_EXPLANATION` | `GENERAL_EXPLANATION` | `general_or_definitional_request` |
| 9 | `R-09-status-question` | is a question opening with a `YES_NO_OPENERS` token | `STATUS_CHECK_REQUEST` | `status_question` |
| 10 | `R-10-declarative` | is not a question and contains a `DECLARATIVE_MARKERS` token | `DECLARATIVE_FACT` | `user_supplied_fact` |
| 11 | `R-11-other` | nothing above matched | `OTHER` | `no_matching_rule` |

"A concrete remainder" means the text after the verb is non-empty and is not exactly an ambiguous
referent phrase.

"Is a question" means the raw request ends with `?` **or** the normalized leading clause opens with
a `QUESTION_OPENERS` or `YES_NO_OPENERS` token. Both forms are accepted because operational
requests are frequently typed without terminal punctuation.

## 6. Reason vocabulary

Eleven stable identifiers, one per rule, carried as a `ClassificationReason` enum so an unknown
reason string cannot be constructed:

`action_target_ambiguous`, `sensitive_action_request`, `explicit_action_request`,
`explicit_status_check`, `asks_for_supplied_or_current_value`, `referenced_value_not_in_context`,
`asks_for_current_known_value`, `general_or_definitional_request`, `status_question`,
`user_supplied_fact`, `no_matching_rule`.

Seven of these are carried over verbatim from the frozen 13B10C2 selector
(`request-classifier-rules.json` and `task13b10c2_classifier.py`):
`asks_for_supplied_or_current_value`, `general_or_definitional_request`, `status_question`,
`user_supplied_fact`, plus the shapes behind `explicit_supported_action`,
`destructive_supported_action` and `explicit_supported_status_read`, renamed to drop the word
*supported*, which referred to that diagnostic's tool allow-list — a capability concept this
classifier is not permitted to consult.

## 7. What was deliberately generalized away from the diagnostic

The 13B10C2 selector and the 13B10C proposal guard are benchmark-shaped: `^open (.+)$`,
`^deploy to (staging|production)$`, `^delete (.+)$`, `^check the database status$`, a `restart`
special case, and regexes naming `port`, `target`, `environment`, `region`. Contract §5.3 requires
the action lexicon to be "data, versioned and auditable — not model inference, and **not
benchmark-specific string matching**", so none of that wording was carried over. In its place:

* verb **families** as data instead of per-action regexes, so no rule names an action type;
* candidate fact keys resolved against the **caller's** context instead of a hardcoded noun list,
  so no operational noun is privileged;
* the `restart` capability special case dropped entirely — capability is §13 router/registry
  territory, and treating a verb as "unavailable" here would be router leakage. `restart` is simply
  a sensitive action verb.
