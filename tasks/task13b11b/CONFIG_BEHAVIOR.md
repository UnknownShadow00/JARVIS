# Execution Configuration Behaviour

**Rule:** the effective mode is `legacy` unless the configuration says otherwise *unambiguously*.
An execution flag must never prevent JARVIS from starting and must never fail into a new path.

## 1. Shape

```yaml
execution:
  mode: "legacy"          # legacy | shadow | control_plane
  shadow_sample_rate: 1.0 # 0.0 – 1.0, only meaningful in shadow
  hermes_brain: false     # model swap, independent of the control plane
```

The whole section is optional. `config.yaml` at commit `2d7a2ec8` had no `execution` section and
loaded to `mode: legacy`; the block was then added explicitly so an operator reading the file can
see which path is live.

## 2. Parser contract

`normalize_execution_section` (`app/config.py`) runs before pydantic validation and coerces the
section to something that always parses. `mode` is `strip()`ed and lowercased, then matched exactly
against the enum values, so `" LEGACY "` is legacy and `"control-plane"` (hyphen) is not a mode and
falls back.

| Input | Effective mode | Other fields | Warning logged |
|---|---|---|---|
| section absent | `legacy` | defaults | no |
| `execution: null` | `legacy` | defaults | no |
| `mode: legacy` | `legacy` | defaults | no |
| `mode: " Shadow "` | `shadow` (parsed, not entered) | defaults | no |
| `mode: banana` / `""` / `5` / `true` / `null` / list / mapping | `legacy` | defaults | yes |
| `mode: hermes` / `enabled` / `selected` / `test` / `control-plane` | `legacy` | defaults | yes |
| section is a string, list or number | `legacy` | defaults | yes |
| unknown key inside the section | `legacy` unless `mode` is valid | unknown key dropped | yes |
| `shadow_sample_rate: -0.5` / `1.5` / `"half"` / `true` | unchanged | `1.0` | yes |
| `hermes_brain: "true"` / `1` / `"yes"` | unchanged | `false` | yes |

Warnings are emitted on the `app.config` logger as
`Invalid execution configuration in <path>: <reason>; using legacy defaults`. The service still
starts: a bad flag is a configuration mistake, not a reason to take JARVIS down.

`true` is rejected for `mode` deliberately — YAML turns a bare `on`/`yes` into a boolean, and a
boolean must never be read as "some mode is on".

## 3. Relationship to `agent.hermes_enabled`

| Setting | Owner | Meaning today | Meaning later |
|---|---|---|---|
| `agent.hermes_enabled` | legacy Hermes task-runner integration | `false`; unchanged by this task | stays the switch for the legacy Hermes surface |
| `execution.mode` | agent execution contract control plane | parsed, never entered | selects which request path handles a turn (P7) |
| `execution.hermes_brain` | model behind the adapter | parsed, unused | swaps the model without swapping the control plane |

For this phase the relationship is one-way and simple: **`hermes_enabled: false` guarantees legacy
behaviour, and nothing in `execution:` can override that**, because no code reads `execution.mode`
at all. When the P7 seam is added, entering the control-plane path must require *both* an explicit
non-legacy `execution.mode` *and*, for a Hermes brain, `execution.hermes_brain: true`; a true
`hermes_enabled` must not be sufficient authority to enter the new path, and this task does not
give it any new meaning.

## 4. Parsing is not entering

`ExecutionConfig.mode` is data. The seam that acts on it does not exist: `tests/execution/
non_activation_test.py` fails if any module outside `app/config.py` imports `app.execution` or
mentions `ExecutionMode`, `ExecutionConfig` or `execution.mode`. That test is the tripwire that
keeps "parsed" and "entered" apart until the phase that deliberately joins them.
