# PipelineStop attempt

Seven fields, sixteen stages and twenty-three reasons match Pipeline V1. Pre-admission stops retain no result; post-S09 downstream stops retain the same admitted result/execution flag and diagnostic state where assembled. No new reason, prose fallback or fabricated result.

First score exposed incorrect AdapterError.code access on three structured hostile-field cases. Existing AdapterError has no code attribute; its fixed message is the owner code. Draft now uses str(error), and all three produce adapter_invalid/invalid_response. Classified IMPLEMENTATION DEFECT and fixed without changing a corpus byte. Full robustness review remains incomplete at P-B06.
