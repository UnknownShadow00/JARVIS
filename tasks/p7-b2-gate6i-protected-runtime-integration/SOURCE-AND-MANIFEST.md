# Source and manifest

Gate6H entry: /home/nexus/.local/share/jarvis-gate6h-authority/release-r1/repo. Expected and verified source manifest `c874b50719a599e4e6a18f051b0395fb45e0b7cc3f0a8338aeca8206cddd9da2`, inventory `57ad124ec88e4e06b40f4d392c3cae27bc5648b010bbfe28d1c92e00754f7fe2` (601 files), evidence seal `3deab83694b8398c184c4deb9a03420760928fa89f63a1d7b4acc88390d7ae74` (245 members), archive `bcc07d09938facd448168e2934815c2f13c3d5f0a81ed2a5a75edcac9a4b4325`. Entry provenance was verified before copying. Original archives/seals were not edited.

Final Gate6I release-r2 candidate: `/home/nexus/.local/share/jarvis-gate6i-runtime/release-r2/repo`.

- Source manifest: `c0aac0e6a33e0dbfcd00616651354ed42c70aa3be22774b83b3348d180a3f461` (39 members; candidate modules/tests plus qualification harness/runner).
- Full inventory: `ed5d0726121e6d5e42717bd367b8da59052b28d791af86b393508dd796b5429e` (606 files).
- Archive: `/home/nexus/.local/share/jarvis-gate6i-runtime/gate6i-release-r2.tar`.
- Archive SHA256: `1aacb61170c83630c5e162cc015d15e90ba1035350d5535c00e369b8f6f9d8a1`.
- Changed/new files relative to Gate6H: 14; production app/ changes: zero.
- Compiled application/candidate/runner Python modules: 144; no bytecode written.

Full source and candidate manifests live in evidence/. Changed source is copied under evidence/source/ with a unified gate6h-to-gate6i.patch. The archive is in the private versioned candidate location, not synchronized as a production backup. Source identities are integrity records, not approvals. The first release-r1 export archive is retained with candidate-r1-identity.json and independently reconstructed R1-EXPORT-FULL-SHA256SUMS. That identity describes export-time content: the unsealed r1 development tree subsequently advanced before the r2 copy, so use run-specific archives for later r1 revisions. Only release-r2 is the final candidate. It adds the FIFO read refusal regression. Intermediate run archives are retained under the same nonproduction parent and each run is checked against its own exact source, never silently relabeled final.

Source manifest paths are repo-relative except qualification/ (root harness) and disposable/ (future runner). FULL-SOURCE-SHA256SUMS is relative to the release-r2 root. Verify every file against both the final inventory and the archive before later provisioning; no Git reset/commit/push is involved.

## Exact historical documents used

| Path | SHA256 |
|---|---|
| tasks/p7-b2-gate6h-release-authority-qualification/FINAL-REPORT.md | 0b0866cbbf64904315f19d31033d6e9e2ed6f9c9616ce426bf06f16dabfd4b02 |
| tasks/p7-b2-gate6h-release-authority-qualification/X1-X11-OPERATOR-DECISION-PACKET.md | f5b3724713021a565ced77f35264b7dd1ed7dc54d7dcc666adc7dd0055229afd |
| tasks/p7-b2-gate6h-release-authority-qualification/MULTI-UID-QUALIFICATION.md | fbc535a867aaf23665279524a17dc5295ce07ce98db4a344cefc7f1492dc22c1 |
| tasks/p7-b2-gate6h-release-authority-qualification/PROTECTED-AUTHORITY-DESIGN.md | fa7e3accc97c9ab03b7df6334c6cff2a2028acb01cb294e2573b599f883fc4e6 |
| tasks/p7-b2-gate6h-release-authority-qualification/ROOT-AND-SIGNER-PROVISIONING-PLAN.md | c72153213620fe1b8c9ecb6828d950d9aeb6c999242ecc3c72a934b5e6d870e3 |
| tasks/p7-b2-gate6h-release-authority-qualification/HUMAN-ONLY-AI-HOST-ATTESTATION.md | 49f37e30ee9678adce9220960ba7e9628e18600e187e2148ee62a425843e995c |
| tasks/p7-b2-gate6h-release-authority-qualification/HUMAN-ONLY-LEGACY-PROVIDER-ATTESTATION.md | 2dfd8c96423a146a174656ad96e877e83f7a5ade53d95ca91b1c2158837efc32 |
| tasks/p7-b2-gate6h-release-authority-qualification/D06-RESOURCE-TOPOLOGY-REQUIREMENTS.md | c3bea7a0f815ebd62bc16fa4f4c83f31d8cd39d037987ed53ee6ff663110c5b0 |

No separate approved disposable environment was found in the local task/candidate records inspected. This does not prove none exists elsewhere; none was assumed or accessed. No privilege probing through sudo/Docker/LXD or new unprivileged namespace claims were used.

Runtime inventory encoding: `evidence/RUNTIME-INVENTORY.json` is canonical JSON of the same606 relative paths/digests; SHA256 `969fcb7aad73c895a801f73d64583f40163feccdbd516764d61179106a1ee98c`. ReleaseIdentityReader binds `bindings.source` to this canonical-map digest (or a separately reviewed installed inventory), not to the textual SHA256SUMS file digest. Both identities must be explicitly reconciled in any future signed release record. Its config binding is the separately approved config-file hash; no production Bindings were provisioned here.
