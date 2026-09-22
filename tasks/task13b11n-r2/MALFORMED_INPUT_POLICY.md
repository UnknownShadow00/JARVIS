# Malformed input
Reject missing keys, unknown keys, duplicate decoded keys, wrong scalar/container types, forbidden nulls, blank names, malformed JSON, markdown fences, trailing tokens, non-object roots, NaN/Infinity/overflow, invalid metadata/count/duplicate IDs and reasoning-key data.
No coercion and no fallback. One malformed later proposal prevents construction of any output.
Decoder errors are caught and replaced outside the handler with a fixed-code AdapterError, so the surfaced error has no raw-document decoder context/cause or .doc attribute.
Interpreter recursion failure fails closed. No arbitrary production resource limits were invented.
