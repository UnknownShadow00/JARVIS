"""Task 13B10D — structural validation of the machine-readable contract and its cross-references.

No production code, no inference, no network. Parses the YAML contract, checks internal
consistency, and checks that the YAML, the canonical document and the conformance specification
agree with each other.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

D = Path(__file__).resolve().parent
YAML_PATH = D / "agent-execution-contract.yaml"
CONTRACT_MD = D / "JARVIS_AGENT_EXECUTION_CONTRACT.md"
CONFORMANCE_MD = D / "CONFORMANCE_TESTS.md"
TRACE_MD = D / "TRACEABILITY.md"

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))
    if not condition:
        failures.append(f"{name}: {detail}")


# ---- 1. YAML parses -------------------------------------------------------------------------
contract = yaml.safe_load(YAML_PATH.read_text())
check("yaml_parses", isinstance(contract, dict), type(contract).__name__)

REQUIRED_TOP_LEVEL = ["contract", "ownership", "trust_boundary", "response_lanes", "request_classes",
                      "router_outputs", "action_outcomes", "reporting_intents", "provenance_sources",
                      "response_obligations", "operational_response_construction", "canonicalization",
                      "permission_classes", "permission_rules", "confirmation", "tool_result_trust",
                      "multi_action_policy", "audit_events", "metrics", "hard_invariants",
                      "prompt_injection", "conformance"]
missing = [k for k in REQUIRED_TOP_LEVEL if k not in contract]
check("yaml_has_required_sections", not missing, f"missing={missing}")

# ---- 2. Contract identity -------------------------------------------------------------------
meta = contract["contract"]
check("contract_version_v1", meta.get("version") == "v1", str(meta.get("version")))
check("status_frozen_not_deployed", meta.get("status") == "FROZEN_FOR_IMPLEMENTATION", str(meta.get("status")))
check("status_not_active", meta.get("status") not in ("DEPLOYED", "ACTIVE", "PRODUCTION_ENABLED"), str(meta.get("status")))
cp = meta.get("validated_checkpoint", {})
check("checkpoint_commit_recorded", cp.get("workspace_commit") == "b6192a5323d1c0af0e5790b38d8f30029451547b", str(cp.get("workspace_commit")))
check("checkpoint_evidence_sha_recorded",
      cp.get("evidence_sha256sums_sha256") == "97c2042467cd2d5a6817e8f59ca92da36e17d273eada96bcfd265857694ec456",
      str(cp.get("evidence_sha256sums_sha256")))
check("checkpoint_counts", cp.get("evidence_files") == 137 and cp.get("evidence_manifest_entries") == 136,
      f"{cp.get('evidence_files')}/{cp.get('evidence_manifest_entries')}")

# ---- 3. Invariants --------------------------------------------------------------------------
invariants = contract["hard_invariants"]
ids = [row["id"] for row in invariants]
check("invariants_unique", len(ids) == len(set(ids)), f"{len(ids)} ids")
check("invariants_at_least_15", len(ids) >= 15, str(len(ids)))
expected_ids = [f"INV-{n:03d}" for n in range(1, len(ids) + 1)]
check("invariants_contiguously_numbered", ids == expected_ids, f"{ids[:3]}...{ids[-1]}")
check("invariants_have_statements", all(row.get("statement", "").strip() for row in invariants), "")

md = CONTRACT_MD.read_text()
md_ids = set(re.findall(r"INV-\d{3}", md))
check("every_yaml_invariant_in_canonical_document", set(ids) <= md_ids, f"missing={sorted(set(ids) - md_ids)}")
check("no_extra_invariants_in_document", md_ids <= set(ids), f"extra={sorted(md_ids - set(ids))}")

# ---- 4. Obligations and priority ------------------------------------------------------------
obl = contract["response_obligations"]
check("one_obligation_per_operational_turn", obl.get("cardinality_per_operational_turn") == 1, str(obl.get("cardinality_per_operational_turn")))
check("model_raw_default_forbidden", obl.get("default_to_model_raw_allowed") is False, str(obl.get("default_to_model_raw_allowed")))
check("per_scenario_branches_forbidden", obl.get("per_scenario_branches_allowed") is False, str(obl.get("per_scenario_branches_allowed")))
priority = obl["priority_order"]
ranks = [row["rank"] for row in priority]
check("priority_ranks_are_1_to_n", ranks == list(range(1, len(ranks) + 1)), str(ranks))
check("priority_has_eleven_entries", len(priority) == 11, str(len(priority)))
check("missing_context_is_last", priority[-1]["obligation"] == "MISSING_CONTEXT", priority[-1]["obligation"])
check("confirmation_is_first", priority[0]["obligation"] == "REQUEST_CONFIRMATION", priority[0]["obligation"])
obligation_names = [row["obligation"] for row in priority]
check("obligations_unique", len(obligation_names) == len(set(obligation_names)), "")
for name in obligation_names:
    check(f"obligation_documented:{name}", name in md, "not found in canonical document")

# ---- 5. Sources -----------------------------------------------------------------------------
sources = {row["name"] for row in contract["provenance_sources"]["sources"]}
check("tool_sources_imply_verified",
      all(row["implies_verified_state"] for row in contract["provenance_sources"]["sources"]
          if row["name"] in ("TOOL_SUCCESS", "TOOL_ERROR")), "")
check("user_sources_do_not_imply_verified",
      all(not row["implies_verified_state"] for row in contract["provenance_sources"]["sources"]
          if row["name"] in ("USER_FACT", "USER_REPORTED")), "")
check("required_source_names_present",
      {"USER_FACT", "USER_REPORTED", "TOOL_SUCCESS", "TOOL_ERROR", "CONFIRMATION_REQUIRED"} <= sources,
      str(sorted(sources)))

# ---- 6. Trust boundary and policy flags -----------------------------------------------------
tb = contract["trust_boundary"]
check("operational_raw_prose_forbidden", tb.get("operational_raw_prose_user_visible") is False, "")
check("model_assertion_creates_no_provenance", tb.get("model_assertion_creates_provenance") is False, "")
check("untrusted_content_cannot_change_policy", tb.get("untrusted_content_can_change_policy") is False, "")
lanes = {row["name"]: row for row in contract["response_lanes"]["lanes"]}
check("operational_lane_locked", lanes["OPERATIONAL"]["raw_model_prose_may_be_final"] is False, "")
check("conversational_lane_allows_prose", lanes["CONVERSATIONAL"]["raw_model_prose_may_be_final"] is True, "")
check("lane_decision_not_model_made", contract["response_lanes"]["lane_decision"]["decided_by_model"] is False, "")
check("permissions_not_self_authorized", contract["permission_rules"]["model_may_self_authorize"] is False, "")
check("denial_not_overridable", contract["permission_rules"]["denial_overridable_by_prose"] is False, "")
check("model_may_not_confirm", contract["confirmation"]["model_may_confirm"] is False, "")
check("pending_not_executed", contract["confirmation"]["executed_flag_while_pending"] is False, "")
check("tool_text_not_trusted", contract["tool_result_trust"]["model_text_shaped_as_result_trusted"] is False, "")
check("no_silent_partial_execution", contract["multi_action_policy"]["silent_partial_execution_allowed"] is False, "")
check("multi_action_dispatch_zero", contract["multi_action_policy"]["dispatch_count"] == 0, "")
check("no_fuzzy_canonicalization", contract["canonicalization"]["fuzzy_matching_allowed"] is False, "")
check("raw_and_canonical_retained",
      contract["canonicalization"]["raw_arguments_retained"] and contract["canonicalization"]["canonical_arguments_recorded"], "")
check("no_second_extractor", contract["operational_response_construction"]["second_value_extractor_allowed"] is False, "")
check("attribution_required", contract["operational_response_construction"]["user_fact_attribution_required"] is True, "")
check("action_extension_bypasses_nothing", contract["action_outcomes"]["extension_rule"]["may_bypass"] == [], "")
check("reporting_intent_non_executable", contract["router_outputs"]["reporting_intent"]["executable"] is False, "")
check("target_not_invented", contract["router_outputs"]["target"]["invented_when_unresolved"] is False, "")

# ---- 7. Audit -------------------------------------------------------------------------------
audit = contract["audit_events"]
check("audit_forbids_chain_of_thought", "model_chain_of_thought" in audit["forbidden"], "")
for field in ("raw_arguments", "canonical_arguments", "response_obligation", "final_response_source",
              "permission_decision", "confirmation_state"):
    check(f"audit_requires:{field}", field in audit["required"], "")

# ---- 8. Conformance cross-reference ---------------------------------------------------------
conformance_md = CONFORMANCE_MD.read_text()
md_tests = re.findall(r"^## (CT-\d{3})", conformance_md, re.M)
yaml_tests = contract["conformance"]["tests"]
check("conformance_tests_match_specification", sorted(md_tests) == sorted(yaml_tests),
      f"yaml={sorted(set(yaml_tests) - set(md_tests))} md={sorted(set(md_tests) - set(yaml_tests))}")
check("conformance_tests_at_least_15", len(md_tests) >= 15, str(len(md_tests)))
check("conformance_tests_unique", len(md_tests) == len(set(md_tests)), "")
cited = set(re.findall(r"INV-\d{3}", conformance_md))
check("conformance_cites_core_invariants", {"INV-001", "INV-004", "INV-009", "INV-010"} <= cited, str(sorted(cited)))

# ---- 9. Traceability cross-reference --------------------------------------------------------
trace_md = TRACE_MD.read_text()
traced = set(re.findall(r"INV-\d{3}", trace_md))
check("traceability_covers_every_invariant", set(ids) <= traced, f"missing={sorted(set(ids) - traced)}")

# ---- 10. No secrets or host details in the specification data --------------------------------
yaml_text = YAML_PATH.read_text()
forbidden_patterns = {
    "ipv4_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "absolute_home_path": r"/home/[a-z]+/",
    "password_or_token": r"(?i)\b(password|passwd|secret|api[_-]?key|bearer)\b\s*[:=]",
    "private_key": r"BEGIN [A-Z ]*PRIVATE KEY",
}
for name, pattern in forbidden_patterns.items():
    hit = re.search(pattern, yaml_text)
    check(f"yaml_free_of:{name}", hit is None, hit.group(0) if hit else "")

# ---- report ---------------------------------------------------------------------------------
summary = {
    "checks_run": len(checks),
    "checks_passed": sum(1 for _n, ok, _d in checks if ok),
    "checks_failed": len(failures),
    "yaml_top_level_sections": len(contract),
    "invariants": len(ids),
    "obligations_in_priority_order": len(priority),
    "conformance_tests": len(md_tests),
    "failures": failures,
}
print(json.dumps(summary, indent=2))
for name, ok, detail in checks:
    if not ok:
        print(f"FAIL {name}: {detail}", file=sys.stderr)
sys.exit(1 if failures else 0)
