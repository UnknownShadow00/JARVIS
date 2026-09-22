# Control metadata ownership
Request.model and Request.turn_id are JARVIS inputs; parse time and ordered proposal IDs are supplied separately by the JARVIS caller. P1 TurnId/is_well_formed_id are reused.
Provider IDs, model names, timestamps, permission/classifier versions and result/confirmation identifiers are rejected as extra structural fields. No echo-retention field exists.
P0 has no proposal ID value object; use its existing str field with P1's shape check and unique case-insensitive UUID identity. No IDs are minted or deterministically invented from provider text.
No correlation fact constitutes authorization.

