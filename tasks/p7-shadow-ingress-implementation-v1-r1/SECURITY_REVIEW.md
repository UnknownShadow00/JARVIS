# Targeted security result

0 observed authority bypasses. Frozen security cases cover fake session/turn/correlation/route/tool/permission, trace equality without authority conversion, mutable payload/P2 source leakage, wrong owner/store/ledger/transport/callable types, malformed settled graphs, immutable public fields, no extra authority keywords, exact import shape and zero consumers.

24 supplemental structural rejection cases test the exact frozen replacement gate on temporary app-source copies. Owner/store/private state, mint/acquisition/write, registry/dispatch/provider/pipeline/binder/transport, dynamic import/service locator, missing validation, extra consumers and observation/ingress presence violations are all rejected. No canonical test assertion was changed to make these pass.

Runtime proofs trap real P2 mutation/acquisition, minting, model/tool/server call edges and I/O. Full existing security/non-activation suites pass with only the one authorized semantic transition. Context/legacy bytes remain unchanged.

Limits: exact Python type checks are not origin authentication or a hostile same-process sandbox. Future authenticated transport/admission, concurrent lifecycle, live provider/scheduling and measured P7 conformance remain outside scope. pip_audit was attempted but unavailable; pip check passed. No dependency-vulnerability PASS or package installation is claimed.
