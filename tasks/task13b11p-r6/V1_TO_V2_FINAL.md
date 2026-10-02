# V1 → final V2

V1 is preserved at 2c87af3425accd4080972b530fdd16dac6291ee4, contract manifest 203eedc6c55b2e68c3697453e0d3d0bde2556e5578ce1cfec9ad41e0998e3919. Pipeline V1 manifest 02d208f7d7f26c9f483f7dcb272620cbb8444426e00b1ee1293193d1dbb5779e. Workspace parent is 8e83309c5dc9fa4efda1cfef1aa12838275a69b0; production baseline db54d615c3ee023d753e86143860c4efdc251230.

P-B02 removes direct ConfirmationRecord exposure across the sealed P4 boundary; only field 15 becomes the settled projection. P-B03 authorizes exact future passive consumer assertions. P-B04 adds the one canonical passive adapter consumer and exact absence-to-presence/non-activation gate. P-B05 R6 selects Option A; C15 zero-proposal expectation is explicitly versioned. Neither V1 nor any prior evidence is edited.

Final row-object comparison: 22 unchanged, 10 changed of 32. Nine P-B02 description-only rows B01–B07/X01–X02; one P-B05 C15 row; zero P-B03/P-B04 admission-row changes. Prior 23/9 was correct before Option A. Nonzero C15 fixture variants preserve pre-existing N24; no new migration parent rows. Detailed old/new objects and reasons are in row-mapping.json.
