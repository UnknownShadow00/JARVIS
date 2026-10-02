# FIXTURE CORPUS — deliberately not frozen

§44 requires the implementation corpus to be frozen and hashed **before** production
pipeline code exists, and 13B11P-R1 requires the admission matrix to be re-verified before
any code is written. Neither was done in this task, on purpose.

The corpus derives from the two frozen matrices, and one of its input fields is unresolved:
`RecordedTurn` field 15. A corpus frozen now would encode nine mode-B rows against a type
that cannot be implemented, and would have to be re-frozen after the repair — which is the
opposite of freeze-first discipline, and exactly the "rewrite expected rows after
observing output" failure §44 exists to prevent. Freezing a corpus that is known to be
wrong would be worse than not freezing one.

Verified and recorded instead, so the next task starts from facts rather than re-derivation:

| Source | Digest | Rows | Verified now |
|---|---|---|---|
| 13B11O-R1 `UPDATED_PIPELINE_MATRIX.md` | `b45a373da04d687d43ab2df60bcdcc6c9da46c769528046f796114830bf86d89` | 47 (`N01`–`N47`) | yes, 0 failures |
| 13B11O-R1 `contradiction-corpus.json` | `d1f8e74966a934f3967cdfea71d9c968e6a058966e6cfa3b7798e265b0e5b012` | 6 (`C01`–`C06`) | yes, 0 failures |
| 13B11P-R1 `admission-matrix.json` | `6b454b2c8d881327b88cef73ae03a6465286bb7fb589e942f1bc3789d76fb434` | 32 (`A01`–`A07`, `B01`–`B07`, `X01`–`X02`, `C01`–`C16`) | yes, 0 failures |
| 13B11O-R1 contract manifest | `02d208f7d7f26c9f483f7dcb272620cbb8444426e00b1ee1293193d1dbb5779e` | 18 entries | yes, 0 failures |
| 13B11P-R1 contract manifest | `203eedc6c55b2e68c3697453e0d3d0bde2556e5578ce1cfec9ad41e0998e3919` | 18 entries | yes, 0 failures |

Of the 32 admission rows, 23 (modes A and C, and the `X02` partial shape) are unaffected by
P-B02 and stand as frozen. Nine (`B01`–`B07`, `X01`, and the `c` term of the mode
derivation) must be restated over the repaired field and re-frozen with a new digest.

The module's absence was proven before any of this and re-proven at exit:
`app/execution/pipeline.py` and `app/brain/pipeline.py` both absent at
`db54d615c3ee023d753e86143860c4efdc251230`.
