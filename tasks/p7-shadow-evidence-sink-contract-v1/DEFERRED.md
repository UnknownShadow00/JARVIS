# Remaining dependencies

D02/D07: attempt identity across retries/concurrency, duplicate key/disposition, recoverable pre-work intent/submission ledger, cancellation/overload, clock/resource isolation, whether to pause on evidence failure. D09/controller: window scope, completeness assessment and formal thresholds. These requirements are recorded; no implementation chosen.

Implementation details within D04 constraints: backend, private leaf layout, exact commit/barrier/framing/concurrency/recovery mechanics, deterministic encoder API and access/backup integration proof. No framework/dependency/install selected. Post-P7 retention/cleanup/export is a separate operator/privacy decision.

D05 authentic current-turn adapter input; D06 provider/model/resource ownership; D01 continuation transport; D08 CT-001/013 acceptance; D10 exact implementation/test exceptions. Producer remains no-clock/no-persistence. Sink does not acquire a latency field without a separate schema freeze. Voice stays outside context/observation coverage. F-AUDIT-01, existing browser D-01/permission/confirmation policies unchanged.
