> **DRAFT — NOT FROZEN. P-B05 prevents final contract and fixture freeze. P-B04 authorization is separately resolved.**

# Matrix migration — first-hand comparison

32 V1 objects loaded from the sealed admission-matrix.json. Exactly 23 row objects remain identical; exactly 9 change only scenario/detail wording to reference the projection. All 32 admitted/mode/stage/outcome/stop values remain identical. No unrelated row moved. A02 retains historical “record” wording verbatim because its absent-field semantics did not change. Machine-readable row-mapping.json records canonical JSON row hashes and changed keys.

| V1 row | V2 row | Status | Reason |
|---|---|---|---|
| A01 | A01 | unchanged | no dependency on repaired observation; row object identical |
| A02 | A02 | unchanged | no dependency on repaired observation; row object identical |
| A03 | A03 | unchanged | no dependency on repaired observation; row object identical |
| A04 | A04 | unchanged | no dependency on repaired observation; row object identical |
| A05 | A05 | unchanged | no dependency on repaired observation; row object identical |
| A06 | A06 | unchanged | no dependency on repaired observation; row object identical |
| A07 | A07 | unchanged | no dependency on repaired observation; row object identical |
| B01 | B01 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| B02 | B02 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| B03 | B03 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| B04 | B04 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| B05 | B05 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| B06 | B06 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| B07 | B07 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| X01 | X01 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| X02 | X02 | repaired | field-15 representation and guard mechanism only; all expected outcomes identical |
| C01 | C01 | unchanged | no dependency on repaired observation; row object identical |
| C02 | C02 | unchanged | no dependency on repaired observation; row object identical |
| C03 | C03 | unchanged | no dependency on repaired observation; row object identical |
| C04 | C04 | unchanged | no dependency on repaired observation; row object identical |
| C05 | C05 | unchanged | no dependency on repaired observation; row object identical |
| C06 | C06 | unchanged | no dependency on repaired observation; row object identical |
| C07 | C07 | unchanged | no dependency on repaired observation; row object identical |
| C08 | C08 | unchanged | no dependency on repaired observation; row object identical |
| C09 | C09 | unchanged | no dependency on repaired observation; row object identical |
| C10 | C10 | unchanged | no dependency on repaired observation; row object identical |
| C11 | C11 | unchanged | no dependency on repaired observation; row object identical |
| C12 | C12 | unchanged | no dependency on repaired observation; row object identical |
| C13 | C13 | unchanged | no dependency on repaired observation; row object identical |
| C14 | C14 | unchanged | no dependency on repaired observation; row object identical |
| C15 | C15 | unchanged | no dependency on repaired observation; row object identical |
| C16 | C16 | unchanged | no dependency on repaired observation; row object identical |

P-B05: unchanged row C15 conflicts with the inherited guard order. Its expectation was not edited. The 23/9 description count is correct but does not prove semantic consistency or fixture realizability.
