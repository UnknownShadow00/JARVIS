# Positive structural transition

The existing test now requires ingress presence and the exact three import statements: `__future__.annotations`, `dataclasses.dataclass`, and the sole `app.execution.shadow_context.SettledShadowTurnContextV1`. Every imported symbol and alias is checked by AST. No additional imports are permitted.

AST bans owner/store/ledger/minting/service-locator names and private attribute access, except the existing dataclass validation hook. Function calls have an exact budget: dataclass decoration, type checks, ValueError construction and exactly one `SettledShadowTurnContextV1.__post_init__(self.context)` validation call. This is reusing existing validation, not allocating another settled value or P2 snapshot.

The complete app reference inventory requires `context_consumers == [ingress]` and `ingress_consumers == []`. All other production files retain the original context bans and gain explicit ingress-consumer bans. Server/API/UI are included in that scan. Observation must remain absent.

24 supplemental virtual-source variants were rejected, including owner/store import/reference, private state, snapshot/mint/write, dynamic import, service locator, provider/pipeline/binder/transport dependencies, removed validation, second context consumer, server ingress consumer, observation presence and absent ingress. These checks use temporary app copies, never modified canonical sources. This is a reviewed structural boundary, not a hostile-Python sandbox.
