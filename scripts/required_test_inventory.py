"""Load reviewed inventory. Acceptance never discovers or rewrites required tests."""
import hashlib
import json
from gauntlet_protocol import InvalidEvidence, case_identifiers


INVENTORY_SHA256 = "bc7359fc23710f82d780943e15c10a45d4df53380884c84c92699c3bc6139f15"


def load_inventory(path, root, mode, *, verify_sources=True, expected_digest=INVENTORY_SHA256):
    def require(value):
        if not value:
            raise InvalidEvidence("invalid_required_inventory")
    try:
        raw = path.read_bytes()
        if expected_digest is not None:
            require(hashlib.sha256(raw).hexdigest() == expected_digest)
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError()
                result[key] = value
            return result
        body = json.loads(raw, object_pairs_hook=unique)
        if verify_sources:
            from test_enrollment import check_enrollment
            policy = check_enrollment(root, root / 'scripts/test_enrollment.json')
            positive_modules = {node.split('::')[0] for name, suite in body['suites'].items()
                                if name != 'probe' and not name.startswith('case:') for node in suite['nodeids']}
            require(positive_modules == {name for name, entry in policy['modules'].items() if entry['disposition'] == 'required'})
        require(set(body) == {'version', 'baseline', 'suites'})
        require(body['version'] == 1 and body['baseline'] == 'b199acede69962919933d5bca364a587b1a2e8ca')
        suite = body['suites'][mode]
        require(set(suite) == {'nodeids', 'sources'})
        nodes = suite['nodeids']
        require(type(nodes) is list and (nodes or mode == 'case:empty') and all(type(n) is str and n.startswith('tests/') and '::test_' in n for n in nodes))
        require(len(nodes) == len(set(nodes)) and nodes == sorted(nodes))
        require(type(suite['sources']) is dict and suite['sources'])
        for name, digest in suite['sources'].items():
            require(type(name) is str and not name.startswith('/') and '..' not in name.split('/'))
            require(type(digest) is str and len(digest) == 64 and set(digest) <= set('0123456789abcdef'))
            if verify_sources:
                if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                    raise InvalidEvidence('inventory_source_mismatch')
        require({n.split('::')[0] for n in nodes} <= suite['sources'].keys())
        identities = case_identifiers(nodes)
        require(len(set(identities.values())) == len(nodes))
        return dict(identities=identities, sha256=hashlib.sha256(raw).hexdigest())
    except InvalidEvidence:
        raise
    except (AssertionError, ValueError, TypeError, KeyError, OSError):
        raise InvalidEvidence('invalid_required_inventory') from None
