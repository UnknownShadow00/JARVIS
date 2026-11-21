# Completed gauntlet handoff

Pass reliability_gauntlet.py its usual new JSON --output path. After it exits successfully, review that file for private archival and run
`python3 -IB scripts/archive_gauntlet_report.py "$REPORT_JSON" --name JARVIS-RUN-gauntlet.zip` from the project root.
Replace RUN with the run identifier. This postprocessor packs one completed report directly on HDD. The gauntlet JSON remains available to existing consumers. Offline installation inputs and R6 work have separate ownership requirements.
