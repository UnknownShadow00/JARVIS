"""File-only local identity/policy gate. No NSS, PAM, sudo, socket or subprocess API."""
import re
from common import need, digest, sha, canonical, integer

SAFE_ENV = {'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'PATH': '/usr/sbin:/usr/bin:/sbin:/bin'}
GENERATED_ENV = {'INVOCATION_ID', 'JOURNAL_STREAM', 'SYSTEMD_EXEC_PID'}

def lines(raw):
    need(type(raw) is bytes and len(raw) <= 1048576, 'policy bound')
    try:
        value = raw.decode('utf-8')
    except UnicodeError:
        raise ValueError('BLOCKED: policy encoding') from None
    need('\x00' not in value and '\\' not in value, 'ambiguous policy continuation')
    return [line.split('#', 1)[0].strip() for line in value.splitlines() if line.split('#', 1)[0].strip()]

def nss_gate(raw):
    entries = {}
    for line in lines(raw):
        need(line.count(':') == 1, 'ambiguous NSS syntax')
        key, value = (x.strip() for x in line.split(':'))
        need(re.fullmatch('[a-z]+', key) and key not in entries, 'duplicate NSS database')
        entries[key] = value
    # Conservative: explicit entries required, no systemd/compat/sss/actions/merge.
    for key in ('passwd', 'group', 'initgroups', 'sudoers', 'hosts', 'netgroup'):
        need(entries.get(key) == 'files', 'local-only NSS not demonstrated')
    return {'kind': 'LOCAL_FILES_NSS_ONLY', 'sha256': sha(raw)}

def local_identity(passwd, groups):
    people = []
    for line in lines(passwd):
        f = line.split(':')
        need(len(f) == 7 and f[0] and f[2].isdecimal() and f[3].isdecimal(), 'passwd schema')
        need(f[1] in ('x', '*', '!'), 'credential-bearing or empty passwd field')
        if f[0] == 'nobody' or int(f[2]) == 65534:
            people.append(f)
    need(len(people) == 1 and people[0][0] == 'nobody' and people[0][2:4] == ['65534','65534'], 'ambiguous existing identity')
    need(people[0][6] in ('/usr/sbin/nologin','/sbin/nologin','/bin/false'), 'interactive account')
    gids = []
    memberships = []
    for line in lines(groups):
        f = line.split(':')
        need(len(f) == 4 and f[0] and f[2].isdecimal() and f[1] in ('x','*','!',''), 'group schema')
        gid = int(f[2])
        if gid == 65534:
            gids.append(gid)
        if 'nobody' in f[3].split(','):
            memberships.append(gid)
    need(gids == [65534] and all(g == 65534 for g in memberships), 'supplementary or ambiguous group')
    return {'uid':65534, 'gid':65534, 'groups':[65534], 'passwd_sha256':sha(passwd), 'group_sha256':sha(groups)}

def policy_gate(nss, passwd, groups, sudo_conf, review):
    nss_gate(nss)
    identity = local_identity(passwd, groups)
    # No sudo invocation exists in R2. Even a custom front-end plugin blocks admission.
    need(lines(sudo_conf) == [], 'custom sudo configuration requires new review')
    for key in ('all_includes_local', 'no_remote_policy', 'no_network_pam', 'no_custom_helpers',
                'vm_authority_denied', 'credentials_denied', 'local_mounts_no_autofs', 'complete_inventory'):
        need(review.get(key) is True, 'incomplete local privilege review')
    need(type(review.get('files')) is dict and review['files'], 'policy inventory absent')
    for path, h in review['files'].items():
        need(type(path) is str and path.startswith('/') and '..' not in path.split('/'), 'policy path')
        digest(h)
    digest(review.get('independent_review_sha256'))
    return {'status':'PASS_LOCAL_POLICY_CONSISTENCY_ONLY', **identity,
            'policy_sha256':sha(canonical(review)), 'nss_sha256':sha(nss),
            'live_origin_verified':False, 'queries_authorized':False}

def environment_gate(manager_values, source_review):
    # Values are compared only in memory; errors/logs never echo names or values.
    need(type(manager_values) is dict and manager_values in ({}, SAFE_ENV), 'environment not allowlisted')
    for key in ('all_sources_reviewed', 'no_dynamic_manager_overrides', 'no_pam', 'no_credentials',
                'no_dropin_commands', 'loader_and_libraries_pinned', 'exclusive_manager_custody'):
        need(source_review.get(key) is True, 'environment source review incomplete')
    digest(source_review.get('independent_review_sha256'))
    return {'policy':'MINIMAL_ENV_R2', 'safe_environment':dict(SAFE_ENV),
            'review_sha256':sha(canonical(source_review)), 'live_origin_verified':False}

def runtime_environment(env):
    need(type(env) is dict and set(SAFE_ENV) <= set(env) <= set(SAFE_ENV)|GENERATED_ENV, 'runtime environment keys')
    need(all(env[k] == v for k,v in SAFE_ENV.items()), 'runtime environment values')
    need(re.fullmatch('[0-9a-f]{32}', env.get('INVOCATION_ID','')) is not None, 'invocation environment')
    if 'JOURNAL_STREAM' in env:
        need(re.fullmatch('[0-9]+:[0-9]+',env['JOURNAL_STREAM']) is not None, 'journal descriptor identity')
    if 'SYSTEMD_EXEC_PID' in env:
        need(re.fullmatch('[1-9][0-9]*',env['SYSTEMD_EXEC_PID']) is not None, 'process environment identity')
    return True
