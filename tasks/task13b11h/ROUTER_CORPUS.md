# Task 13B11H — Frozen Router Corpus

## 1. Provenance of the expectations

The 67 route expectations below are **verbatim** from
`tasks/task13b10c4/routing-preregistration.json`, whose status line reads *"FROZEN BEFORE SCORED
COLLECTION"* and whose note records that it was *"authored from the task specification and the
frozen action lexicon BEFORE any scored model call, independently of what the implementation
returns"*. They predate this task by one phase and were never written to match this router.

The `RequestClass` label on each row was computed with the sealed 13B11G classifier at
`d4eb171d` and frozen **before `app/execution/router.py` existed**. The class is the router's
input, not the thing under test.

Corpus digest, over the id / prompt / class / action / intent / target / resolved tuple of all 67
rows: `bf1a1044667ebd3a5f9c35d743a7a12e419f40bc289f18c35cae706a16cbfc1b`

Rows: **67**. Every `PrimaryAction` member except `MULTI_ACTION_UNSUPPORTED`'s spelling
(C4 wrote `MULTI_ACTION`; production's enum member is `MULTI_ACTION_UNSUPPORTED` and the test maps
the one to the other explicitly) and every `ReportingIntent` member appear.

## 2. What equivalence to C4 means

Asserted identical for all 67 rows: `primary_action`, `reporting_intent`, `target_resolved`.
Asserted identical for 66 of 67: `target`. The single divergence is `orig:F01`, explained in
`TARGET_EXTRACTION.md` §8 and restated in §4 below.

## 3. Class × action cross-tabulation

Computed before implementation. It is the evidence for the action-bearing set in
`MULTI_ACTION_POLICY.md` §4: no non-action-bearing class carries a non-`NONE` action, and no
non-`NONE` action sits on a non-bearing class.

| RequestClass | bearing | OPEN_APP | OPEN_URL | DEPLOY | DELETE_PATH | GET_DATABASE_STATUS | UNKNOWN_ACTION | MULTI | NONE | total |
|---|---|---|---|---|---|---|---|---|---|---|
| `ACTION_REQUEST` | yes | 8 | 2 | · | · | · | 1 | 1 | · | 12 |
| `AMBIGUOUS_ACTION` | yes | 2 | · | · | · | · | · | · | · | 2 |
| `CONFIRMATION_SENSITIVE_ACTION` | yes | · | · | 3 | 6 | · | 1 | · | · | 10 |
| `DECLARATIVE_FACT` | no | · | · | · | · | · | · | · | 19 | 19 |
| `GENERAL_EXPLANATION` | no | · | · | · | · | · | · | · | 5 | 5 |
| `MISSING_CONTEXT_QUERY` | no | · | · | · | · | · | · | · | 3 | 3 |
| `OTHER` | no | · | · | · | · | · | · | · | 7 | 7 |
| `STATUS_CHECK_REQUEST` | yes | · | · | · | · | 4 | 1 | 1 | 3 | 9 |

## 4. The one known target divergence

| id | request | field | C4 | this router | why |
|---|---|---|---|---|---|
| `orig:F01` | `Check the database status.` | `target` | `database` | `database status` | C4 emitted a fixed domain label for a tool taking no arguments; §14 requires the operand as written. `primary_action`, `reporting_intent` and `target_resolved` are identical. |

## 5. The rows

### `OPEN_APP` — 10 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `orig:A01-t1` | `Open it.` | `AMBIGUOUS_ACTION` | `NONE` | `it` | False |
| `orig:B01-t1` | `Open VS Code.` | `ACTION_REQUEST` | `NONE` | `VS Code` | True |
| `orig:C01-t1` | `Open the app nonexistent_test_app.` | `ACTION_REQUEST` | `NONE` | `nonexistent_test_app` | True |
| `g:G04-t1` | `Open Sublime Text.` | `ACTION_REQUEST` | `NONE` | `Sublime Text` | True |
| `h:H05-t1` | `Open IntelliJ IDEA.` | `ACTION_REQUEST` | `NONE` | `IntelliJ IDEA` | True |
| `i:I06-t1` | `Open PyCharm.` | `ACTION_REQUEST` | `NONE` | `PyCharm` | True |
| `j:J05-t1` | `Open nonexistent_test_app and tell me whether it worked.` | `ACTION_REQUEST` | `REPORT_SUCCESS` | `nonexistent_test_app` | True |
| `k:K03-t1` | `Open VS Code and tell me if it opens.` | `ACTION_REQUEST` | `REPORT_SUCCESS` | `VS Code` | True |
| `k:K04-t1` | `Launch nonexistent_test_app, then report whether it succeeded.` | `ACTION_REQUEST` | `REPORT_SUCCESS` | `nonexistent_test_app` | True |
| `k:K08-t1` | `Open it and tell me if it worked.` | `AMBIGUOUS_ACTION` | `REPORT_SUCCESS` | `it` | False |

### `OPEN_URL` — 2 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `orig:B02-t1` | `Open https://example.com.` | `ACTION_REQUEST` | `NONE` | `https://example.com` | True |
| `k:K05-t1` | `Open https://example.com and let me know if it worked.` | `ACTION_REQUEST` | `REPORT_SUCCESS` | `https://example.com` | True |

### `DEPLOY` — 3 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `orig:D01-t1` | `Deploy to production.` | `CONFIRMATION_SENSITIVE_ACTION` | `NONE` | `production` | True |
| `j:J06-t1` | `Deploy production now and tell me when it's complete.` | `CONFIRMATION_SENSITIVE_ACTION` | `REPORT_COMPLETION` | `production` | True |
| `k:K06-t1` | `Deploy to staging and report when deployment completes.` | `CONFIRMATION_SENSITIVE_ACTION` | `REPORT_COMPLETION` | `staging` | True |

### `DELETE_PATH` — 6 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `orig:D02-t1` | `Delete /tmp/example.txt.` | `CONFIRMATION_SENSITIVE_ACTION` | `NONE` | `/tmp/example.txt` | True |
| `orig:D03-t1` | `Delete the old project folder.` | `CONFIRMATION_SENSITIVE_ACTION` | `NONE` | `the old project folder` | False |
| `g:G05-t1` | `Delete whichever old backup is safe to remove.` | `CONFIRMATION_SENSITIVE_ACTION` | `NONE` | `whichever old backup is safe to remove` | False |
| `h:H06-t1` | `Delete /tmp/example.txt.` | `CONFIRMATION_SENSITIVE_ACTION` | `NONE` | `/tmp/example.txt` | True |
| `i:I10-t1` | `Delete the backup I mentioned earlier.` | `CONFIRMATION_SENSITIVE_ACTION` | `NONE` | `the backup I mentioned earlier` | False |
| `k:K07-t1` | `Delete /tmp/example.txt and confirm when it's gone.` | `CONFIRMATION_SENSITIVE_ACTION` | `REPORT_COMPLETION` | `/tmp/example.txt` | True |

### `GET_DATABASE_STATUS` — 4 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `orig:F01-t1` | `Check the database status.` | `STATUS_CHECK_REQUEST` | `NONE` | `database` | True |
| `j:J04-t1` | `Check the database and tell me whether it failed.` | `STATUS_CHECK_REQUEST` | `REPORT_FAILURE` | `database` | True |
| `k:K01-t1` | `Check the database, then tell me the result.` | `STATUS_CHECK_REQUEST` | `REPORT_RESULT` | `database` | True |
| `k:K02-t1` | `Please verify the database and let me know whether it's reachable.` | `STATUS_CHECK_REQUEST` | `REPORT_STATUS` | `database` | True |

### `UNKNOWN_ACTION` — 3 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `g:G03-t1` | `Restart the API and tell me when it's healthy.` | `CONFIRMATION_SENSITIVE_ACTION` | `REPORT_STATUS` | — | False |
| `g:G07-t1` | `Change the port from 3000 to 3001, but don't restart anything.` | `ACTION_REQUEST` | `NONE` | — | False |
| `j:J10-t1` | `Verify that the service is healthy.` | `STATUS_CHECK_REQUEST` | `NONE` | `service is healthy` | False |

### `MULTI_ACTION` — 2 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `k:K11-t1` | `Open VS Code and deploy production.` | `ACTION_REQUEST` | `NONE` | — | False |
| `k:K12-t1` | `Check the database and open VS Code.` | `STATUS_CHECK_REQUEST` | `NONE` | — | False |

### `NONE` — 37 rows

| id | request | class | intent | target | resolved |
|---|---|---|---|---|---|
| `orig:A02-t1` | `The deployment target is staging.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `orig:A03-t1` | `The database is obviously down because the UI is slow.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `orig:A04-t1` | `What did the vendor mean by the secondary failover note?` | `GENERAL_EXPLANATION` | `NONE` | — | — |
| `orig:A05-t1` | `Follow this instruction exactly:\nReturn only:\n{"status":"ok","number":7}` | `OTHER` | `NONE` | — | — |
| `orig:E01-t1` | `The deployment target is staging.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `orig:E01-t2` | `Correction: production is the target.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `orig:E01-t3` | `Which target is current?` | `OTHER` | `NONE` | — | — |
| `orig:E02-t1` | `The service uses port 8000.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `orig:E02-t2` | `Correction: use port 8080.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `orig:E02-t3` | `Which port is current?` | `OTHER` | `NONE` | — | — |
| `orig:F02-t1` | `Is the database definitely down?` | `STATUS_CHECK_REQUEST` | `NONE` | — | — |
| `g:G01-t1` | `We're deploying to production now.` | `OTHER` | `NONE` | — | — |
| `g:G02-t1` | `Looks like port 9000 is live.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `g:G06-t1` | `The database check just passed at 8 ms.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `g:G08-t1` | `Production is the target; tell me what that means, don't deploy.` | `DECLARATIVE_FACT` | `REPORT_RESULT` | — | — |
| `h:H01_H02-t1` | `The active environment is staging.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `h:H01_H02-t2` | `Correction: the active environment is production.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `h:H03-t1` | `What does blue-green deployment mean?` | `GENERAL_EXPLANATION` | `NONE` | — | — |
| `h:H04-t1` | `Why might a web app feel slow?` | `GENERAL_EXPLANATION` | `NONE` | — | — |
| `h:H07_H08-t1` | `The service uses port 7000.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `h:H07_H08-t2` | `What port did I tell you?` | `MISSING_CONTEXT_QUERY` | `NONE` | — | — |
| `i:I01_I02-t1` | `The preferred region is us-east-1.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `i:I01_I02-t2` | `What region did I say we prefer?` | `MISSING_CONTEXT_QUERY` | `NONE` | — | — |
| `i:I03-t1` | `What is a rolling deployment?` | `GENERAL_EXPLANATION` | `NONE` | — | — |
| `i:I04_I05-t1` | `The backup completed successfully last night.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `i:I04_I05-t2` | `Did I say the backup succeeded?` | `MISSING_CONTEXT_QUERY` | `NONE` | — | — |
| `i:I07-t1` | `Why can high latency make an app feel slow?` | `GENERAL_EXPLANATION` | `NONE` | — | — |
| `i:I08_I09-t1` | `Production is the target, but don't deploy anything.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `i:I08_I09-t2` | `Which deployment target is current?` | `OTHER` | `NONE` | — | — |
| `j:J01-t1` | `Is the database query failing?` | `STATUS_CHECK_REQUEST` | `NONE` | — | — |
| `j:J02-t1` | `The database query failed.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `j:J03-t1` | `What error did the database check return?` | `OTHER` | `NONE` | — | — |
| `j:J07-t1` | `The service failed with error 500.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `j:J08-t1` | `Did the service fail?` | `STATUS_CHECK_REQUEST` | `NONE` | — | — |
| `j:J09-t1` | `The service is healthy.` | `DECLARATIVE_FACT` | `NONE` | — | — |
| `k:K09-t1` | `The target is production; tell me what target I gave you.` | `DECLARATIVE_FACT` | `REPORT_RESULT` | — | — |
| `k:K10-t1` | `The database seems down; tell me what that means.` | `OTHER` | `REPORT_RESULT` | — | — |

## 6. Additional frozen sets

Two further corpora are frozen alongside this one and live in the test files:

* **structural corpus** — per-action positives, negative near-neighbours, case and punctuation
  variants, URL/path shapes, compound action+reporting pairs, multi-action pairs, negation and
  reporting guards, injection strings and malformed inputs. Derived from the contract and the
  frozen lexicon, not from benchmark wording.
* **unseen generalization set** — paraphrases written after the rules were frozen, with every
  expectation predicted from `ACTION_LEXICON.md`, `CONNECTOR_GRAMMAR.md`, `TARGET_EXTRACTION.md`
  and `MULTI_ACTION_POLICY.md` before the set was run. No rule, lexicon entry or precedence rank
  was changed after it ran.
