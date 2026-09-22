# Malformed Input Policy — Required Decision

Fail-closed is mandatory, but the precise policy is not frozen. A prerequisite contract must state
the disposition of malformed JSON/objects, missing and null fields, wrong scalar/container types,
unknown and extra fields, duplicate keys, conflicting proposal representations, invalid argument
JSON, empty names, and multiple proposals.

Until that decision exists, no parser may guess, coerce or choose the value that grants more
authority. This task created no parser and therefore no fail-open path.
