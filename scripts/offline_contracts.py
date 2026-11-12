"""Run preserved CLI contracts with additive public-fixture adapters only.

Historical files are never rewritten. Their copies must include the new root
guard/workflow, otherwise a positive control would test a truncated checkout.
"""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ADDITIONS = "'conftest.py','.github/workflows/tests.yml',"


def adapted_source(kind):
    paths = {
        'gate22': 'tasks/jarvis-v2-baseline-coverage-remediation-r2/check_gate_contracts.py',
        'adversaries11': 'tasks/jarvis-v2-baseline-coverage-remediation-r2/check_adversaries.py',
        'attacks12': 'tasks/jarvis-v2-final-integration-rehearsal-r2/replay_audit_attacks.py',
    }
    path = ROOT / paths[kind]
    body = path.read_text()
    anchor = "'pytest.ini','config.yaml.example'" if kind != 'gate22' else "'config.yaml.example','pytest.ini'"
    if body.count(anchor) != 1:
        raise ValueError('historical_contract_adapter_mismatch')
    body = body.replace(anchor, PUBLIC_ADDITIONS + anchor, 1)
    return path, body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=('gate22', 'adversaries11', 'attacks12'))
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    path, body = adapted_source(args.kind)
    if args.kind == 'gate22':
        sys.argv = [str(path), '--source-root', str(args.source_root), '--output-dir', str(args.output_dir)]
    elif args.kind == 'attacks12':
        sys.argv = [str(path), str(args.source_root), str(args.output_dir)]
    else:
        sys.argv = [str(path), str(args.output_dir), str(args.source_root)]
    # Preserve the helper's original __file__/Git repository for the pinned
    # b199ace historical runner; mutations happen ONLY in disposable clones.
    exec(compile(body, str(path), 'exec'), {'__name__': '__main__', '__file__': str(path)})


if __name__ == '__main__':
    main()
