# Binding ownership

| Value | Authority | Composer action |
|---|---|---|
| Request and correlation | P1 JARVIS ingress | Preserve exact IDs and text; reject inconsistent associations |
| Classifier result | P2 classifier v2 | Invoke/consume existing result; never parse verbs again |
| Lane | Existing lane module | Consume existing result; do not derive a new policy |
| Action, route, target | P3 router | Use exact resolved result; no client/model override |
| Raw-to-canonical arguments and version | P3 canonicalizer | Invoke existing canonicalizer; do not copy alias rules |
| Capability | P4 `ACTION_CAPABILITY` closed pair | Admit only the two reviewed V1 pairs |
| Tool key and declared metadata | JARVIS registry declarations through passive snapshot | Require exact reviewed key and handler shape; no registry API call |
| Permission | P4 permission engine and JARVIS approval mode | Supply `PermissionRequest`; P7 calls `decide` |
| Confirmation | P5 settled projection owner | Not part of binder; no machine/store import |
| Proposal/model draft | Hermes adapter | Not part of binder; untrusted comparison input |
| Result/replay | Trusted result continuation owner | Not part of binder; no execution authority |

The producer composes settled values. The crosswalk in `ADMITTED_MAPPING_V1.md` is the only new V1 mapping authority. It does not replace any owner listed above.
