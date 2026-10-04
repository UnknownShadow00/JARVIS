# Mode and activation

`ExecutionConfig` in `app/config.py:227-239` parses `legacy|shadow|control_plane`; `config.yaml:170-174` is `legacy`, sample rate 1.0, `hermes_brain: false`; `agent.hermes_enabled: false`. Only `legacy` is currently wired. Frozen `task13b11a/FEATURE_FLAG_AND_ROLLBACK.md:16-35` requires one mode read per turn, default/fallback legacy, and explicit `execution.mode: shadow` activation. `shadow_sample_rate` is a config value, not a frozen measurement window or sampling algorithm.

Future operator activation requires an approved provider decision if live model is used, audit/failure contract, ingress implementation and a no-side-effect gate. Disable via `execution.mode: legacy` and restart per existing rollback plan. No auto-enable, UI/client override, or `control_plane` activation. Unparseable mode must remain legacy. How shadow work is scheduled and sampled without delaying legacy is unresolved before wiring.
