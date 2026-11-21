"""Pack one owner-reviewed, completed offline engineering gauntlet report on the HDD."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def archive(report_path, name):
    path = report_path.absolute()
    if path != path.resolve(strict=True) or not path.is_file() or path.suffix != '.json':
        raise ValueError('Select the regular JSON output of reliability_gauntlet.py')
    data = path.read_bytes()
    result = json.loads(data)
    count = result['collected']
    session = result['session']
    if not (result['child_exit_code'] == 0 and session['pytest_exit_code'] == 0
            and session['collected_count'] == count
            and all(session[k] is True for k in ('started', 'collected', 'finished'))
            and all(session[k] is False for k in ('interrupted', 'internal_error', 'collection_error', 'unexpected_report'))
            and result['qualification'] == 'OFFLINE_ENGINEERING_ONLY' and result['status'] == 'PASS'
            and type(result['gate_exit_code']) is int and result['gate_exit_code'] == 0
            and result['reason'] == 'complete' and result['timed_out'] is False
            and type(count) is int and count > 0 and count == result['executed'] == result['attempted']
            and result['counts'] == {'PASS': count, 'FAIL': 0, 'ERROR': 0, 'SKIP': 0, 'INCOMPLETE': 0}
            and len(result['scenarios']) == count and all(s['complete'] is True and s['status'] == 'PASS'
            and s['timed_out'] is False for s in result['scenarios'])):
        raise ValueError('Gauntlet report is incomplete or did not pass')
    # Give the publisher the exact bytes checked above, even if another process replaces the input.
    with tempfile.TemporaryDirectory(prefix='jarvis-report-') as tmp:
        (Path(tmp) / 'gauntlet-report.json').write_bytes(data)
        subprocess.run([str(Path.home() / '.local/bin/nexus-archive'), 'pack', '--verified',
                        '--to', 'jarvis-evidence', '--base', tmp, '--name', name, 'gauntlet-report.json'], check=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    p.add_argument('--name', required=True)
    args = p.parse_args()
    try:
        archive(args.report, args.name)
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        p.exit(1, f'JARVIS archival stopped: {exc}\n')
