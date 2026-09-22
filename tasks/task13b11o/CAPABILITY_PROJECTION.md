# Capability projection

D-08 is binding. Abstract PrimaryAction vocabulary, RouterContext defaults, model-visible ToolSchema descriptors and a model-named tool are four distinct things; none alone establishes a live capability.

Frozen P4 action/capability pairs: OPEN_APP → apps.open and OPEN_URL → browser.open. The policy table is version 1; apps.open requires confirmation, browser.open/browser.search retain their current frozen outcomes. No browser D-01 reinterpretation is made. DEPLOY, DELETE_PATH and GET_DATABASE_STATUS cannot acquire live implementations through a synthetic descriptor.

Proposed passive linkage is caller-supplied static capability availability plus an explicit RouterContext, intersected with the existing P4 policy facts rather than model descriptions. No registry import or runtime discovery. Caller evidence for satisfied_constraints must identify the deterministic check that discharged it; unverified/model claims never populate that set. No new network validator or permission grant is specified.

O-B01 blocks the next link: capability identifiers such as apps.open are not the canonicalizer's tool namespace apps, nor an execution argument schema. The current APIs do not define a complete closed schema for action/tool/target/extra arguments or perform route-to-proposal matching. Inferring `apps.open` by concatenating model fields, dropping extra arguments or borrowing legacy/harness argument extraction would create unreviewed authority.

Supported-read conformance is also constrained by the current vocabulary: P4 has read-only rows such as system_stats.read, but P3 has no corresponding routable action; GET_DATABASE_STATUS's capability is unregistered. A P4-only read fixture is valid component coverage, not proof of a supported P7 end-to-end read. Do not omit primary_action from a routed request, invent a new enum or register a synthetic live capability to make that row pass. Matrix M04 explicitly records this gap.
