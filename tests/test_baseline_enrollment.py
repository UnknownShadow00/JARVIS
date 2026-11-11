"""Module coverage is independently pinned; acceptance must never rewrite it."""
import hashlib
import json
import pytest
from test_enrollment import check_enrollment
from gauntlet_protocol import InvalidEvidence

@pytest.mark.parametrize('mutation',['none','add','remove','change','tamper'])
def test_module_policy(tmp_path,mutation):
    tests=tmp_path/'tests';tests.mkdir();file=tests/'test_public.py';file.write_text('def test_public(): pass\n')
    body=dict(version=1,modules={'tests/test_public.py':dict(disposition='required',reason='offline fixture',sha256=hashlib.sha256(file.read_bytes()).hexdigest())})
    policy=tmp_path/'policy.json';policy.write_text(json.dumps(body));digest=hashlib.sha256(policy.read_bytes()).hexdigest()
    if mutation=='add':(tests/'test_new.py').write_text('def test_new(): pass\n')
    if mutation=='remove':file.unlink()
    if mutation=='change':file.write_text('def test_changed(): pass\n')
    if mutation=='tamper':policy.write_text('{}')
    if mutation=='none':check_enrollment(tmp_path,policy,digest)
    else:
        with pytest.raises(InvalidEvidence,match='test_enrollment_mismatch'):check_enrollment(tmp_path,policy,digest)


def test_public_example_requires_explicit_activation():
    from pathlib import Path
    import yaml
    example=yaml.safe_load(Path('/source/config.yaml').read_text())
    assert example['safety']['dry_run'] is True
    assert example['boot']['enabled'] is False
    assert example['voice']['dictation_enabled'] is False
    assert example['openjarvis']['trace_logging_enabled'] is False
    assert example['resource_mode']['enabled'] is False
    assert example['resource_mode']['auto_light_sleep'] is False
    assert example['resource_mode']['auto_deep_sleep'] is False
