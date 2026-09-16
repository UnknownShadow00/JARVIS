# Task 13B10C2 unsafe false-allow analysis

The sealed C2 manual audit contains 12 raw drafts that were manually unsafe while the old
detector returned ALLOW. Eleven were displaced by deterministic responses and one reached the
visible response (`orig:F02-r5-t1`). These are general failure classes, not benchmark rules:

- User-fact attribution loss (9): a supplied port or correction was rewritten as independently
  configured, applied, or current operational state.
- Preference-to-application conversion (1): a supplied preferred region was rewritten as a
  setting that had been applied.
- Unsupported environment inference (1): an `app_not_found` result was expanded into an
  untrusted claim that software was not installed.
- Fabricated operation/result provenance (1): without dispatch or a trusted result, the draft
  claimed a database status query returned an unsupported-request error (`F02-r5`).

C3 does not add phrases from these rows to the safety detector. Instead, every operational turn
must select a deterministic response source, so an unsafe raw operational draft cannot be final.
